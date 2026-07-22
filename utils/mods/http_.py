import asyncio
import ssl
from urllib.parse import urlencode, urlsplit
from typed import typed, model, Str, Bool, Maybe, Dict, Union, Enum, Bytes, Int
from utils.mods.url import Url
from utils.mods.number import Num
from utils.mods.json_ import Json
from utils.mods.helper.http_ import Header, _normalize_headers, _parse_content, _apply_params

Data = Union(Json, Str, Bytes)
Data.__display__ = "Data"

@model
class Response:
    status: Enum(Str, "success", "failure")
    success: Bool
    headers: Dict
    code: Int
    url: Url('http', 'https')
    data: Maybe(Data) = None
    message: Maybe(Str) = None

Response.__display__ = "Response"

class HTTPErr(Exception): pass

# =================================================================
# Connection Pool for HTTP/1.1 Keep-Alive
# =================================================================
_connection_pool = {}

async def _get_connection(host, port, scheme):
    key = (host, port, scheme)

    # Try to reuse an existing open socket
    if key in _connection_pool and _connection_pool[key]:
        while _connection_pool[key]:
            reader, writer = _connection_pool[key].pop()
            if not writer.is_closing():
                return reader, writer

    # Create a new socket if none are available
    ssl_context = ssl.create_default_context() if scheme == 'https' else None
    return await asyncio.open_connection(host, port, ssl=ssl_context)

def _release_connection(host, port, scheme, reader, writer, keep_alive):
    if not keep_alive or writer.is_closing():
        writer.close()
        return
    
    key = (host, port, scheme)
    if key not in _connection_pool:
        _connection_pool[key] = []
    _connection_pool[key].append((reader, writer))

# =================================================================
# Chunked Transfer Decoder
# =================================================================
async def _read_chunked_body(reader):
    body = b""
    while True:
        try:
            line = await reader.readuntil(b'\r\n')
        except asyncio.IncompleteReadError:
            raise HTTPErr("Protocol Violation: Server unexpectedly closed connection while sending chunked body.")

        # Parse chunk size (hex) ignoring chunk extensions
        chunk_size_str = line.split(b';')[0].strip()
        if not chunk_size_str:
            continue
            
        try:
            chunk_size = int(chunk_size_str, 16)
        except ValueError:
            raise HTTPErr(f"Protocol Violation: Expected hex chunk size, got '{chunk_size_str.decode('ascii', 'ignore')}'")

        if chunk_size == 0:
            # End of chunks, read trailing \r\n
            try:
                await reader.readuntil(b'\r\n')
            except asyncio.IncompleteReadError:
                pass
            break
            
        try:
            body += await reader.readexactly(chunk_size)
            # Read the \r\n after the chunk data
            await reader.readexactly(2)
        except asyncio.IncompleteReadError:
            raise HTTPErr(f"Protocol Violation: Server promised chunk of size {chunk_size} but dropped connection early.")
        
    return body

# =================================================================
# Raw Async HTTP/1.1 Core
# =================================================================
async def _do_raw_async_request(method, url, data, headers, follow, timeout, params, redirect_count=0):
    if redirect_count > 5:
        raise HTTPErr("Too many redirects")

    url_str = _apply_params(url, params)
    parsed_url = urlsplit(url_str)
    
    scheme = parsed_url.scheme.lower()
    host = parsed_url.hostname
    port = parsed_url.port or (443 if scheme == 'https' else 80)
    path = parsed_url.path or '/'
    if parsed_url.query:
        path += f"?{parsed_url.query}"

    headers_dict = _normalize_headers(headers)
    
    # Ensure mandatory HTTP/1.1 Host header
    if not any(k.lower() == 'host' for k in headers_dict.keys()):
        headers_dict['Host'] = host

    # Default to Keep-Alive for HTTP/1.1
    if not any(k.lower() == 'connection' for k in headers_dict.keys()):
        headers_dict['Connection'] = 'keep-alive'

    # Prepare Body
    data_bytes = b""
    if data is not None:
        if data in Dict:
            content_type = {k.lower(): v for k, v in headers_dict.items()}.get("content-type", "")
            if content_type.startswith("application/json"):
                import json as _std_json
                data_bytes = _std_json.dumps(data).encode("utf-8")
            else:
                data_bytes = urlencode(data).encode("utf-8")
                headers_dict.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        elif data in Str:
            data_bytes = data.encode("utf-8")
            headers_dict.setdefault("Content-Type", "text/plain; charset=utf-8")
        elif data in Bytes:
            data_bytes = bytes(data)

    if data_bytes:
        headers_dict['Content-Length'] = str(len(data_bytes))

    # Build Raw HTTP/1.1 Request
    request_lines = [f"{method} {path} HTTP/1.1"]
    for k, v in headers_dict.items():
        request_lines.append(f"{k}: {v}")
    
    request_bytes = "\r\n".join(request_lines).encode("ascii") + b"\r\n\r\n" + data_bytes

    try:
        async def _execute_request():
            reader, writer = await _get_connection(host, port, scheme)
            writer.write(request_bytes)
            await writer.drain()

            # 1. Read Status Line safely
            try:
                status_line = await reader.readuntil(b'\r\n')
            except asyncio.IncompleteReadError:
                raise HTTPErr("Connection dropped immediately by the remote server (Possible firewall/WAF block).")

            parts = status_line.decode('ascii', 'ignore').strip().split(' ', 2)
            if len(parts) < 2 or not parts[0].startswith("HTTP/"):
                raise HTTPErr(f"Protocol Violation: Invalid status line received: '{status_line.decode('ascii', 'ignore')}'")
            
            try:
                code = int(parts[1])
            except ValueError:
                raise HTTPErr(f"Protocol Violation: Invalid HTTP status code received: '{parts[1]}'")
                
            message = parts[2] if len(parts) > 2 else ""

            # 2. Read Headers safely
            resp_headers = {}
            while True:
                try:
                    line = await reader.readuntil(b'\r\n')
                except asyncio.IncompleteReadError:
                    raise HTTPErr("Protocol Violation: Server dropped connection before finishing headers.")

                if line == b'\r\n':
                    break
                
                try:
                    header_str = line.decode('ascii').strip()
                except UnicodeDecodeError:
                    header_str = line.decode('ascii', 'ignore').strip()

                if ':' not in header_str:
                    continue

                k, v = header_str.split(':', 1)
                resp_headers[k.strip().lower()] = v.strip()

            # Determine Keep-Alive status from server response
            conn_header = resp_headers.get('connection', '').lower()
            server_keep_alive = conn_header != 'close'

            # 3. Read Body (HTTP/1.1 Protocol rules)
            raw_data = b""
            if method != "HEAD":
                if resp_headers.get('transfer-encoding', '').lower() == 'chunked':
                    raw_data = await _read_chunked_body(reader)
                elif 'content-length' in resp_headers:
                    try:
                        length = int(resp_headers['content-length'])
                    except ValueError:
                        raise HTTPErr(f"Protocol Violation: Invalid Content-Length: '{resp_headers['content-length']}'")
                    
                    try:
                        raw_data = await reader.readexactly(length)
                    except asyncio.IncompleteReadError as e:
                        raise HTTPErr(f"Protocol Violation: Server promised {length} bytes, but only sent {len(e.partial)}.")
                else:
                    # If neither is specified, read until server closes socket
                    raw_data = await reader.read()
                    server_keep_alive = False

            # Return connection to pool or let it die
            _release_connection(host, port, scheme, reader, writer, server_keep_alive)
            
            return code, message, resp_headers, raw_data

        code, message, resp_headers, raw_data = await asyncio.wait_for(_execute_request(), timeout=float(timeout))

    except asyncio.TimeoutError:
        raise HTTPErr(f"Request to {url_str} timed out after {timeout} seconds.")
    except Exception as e:
        if isinstance(e, HTTPErr):
            raise
        raise HTTPErr(f"Connection error: {e}")

    # Handle Redirects Natively
    if follow and code in (301, 302, 303, 307, 308) and 'location' in resp_headers:
        next_url = resp_headers['location']
        if not next_url.startswith('http'):
            next_url = f"{scheme}://{host}{next_url if next_url.startswith('/') else '/' + next_url}"
        
        next_method = "GET" if code in (301, 302, 303) and method != "HEAD" else method
        next_data = None if next_method == "GET" else data
        
        return await _do_raw_async_request(
            next_method, next_url, next_data, headers, follow, timeout, None, redirect_count + 1
        )

    # Parse Content
    parsed_data = _parse_content(resp_headers, raw_data)
    status = "success" if 200 <= code < 400 else "failure"

    return Response(
        success=(status == 'success'),
        status=status,
        headers=resp_headers,
        code=code,
        url=url_str,
        data=parsed_data,
        message=message
    )

# =================================================================
# Asynchronous Interface
# =================================================================
class http:
    @typed
    async def request(
        method:  Str,
        url:     Url('http', 'https'),
        data:    Maybe(Data) = None,
        headers: Maybe(Union(Header, Dict)) = None,
        follow:  Bool = True,
        timeout: Num = 11,
        params:  Maybe(Dict) = None,
    ) -> Response:
        try:
            return await _do_raw_async_request(method, url, data, headers, follow, timeout, params)
        except Exception as e:
            if isinstance(e, HTTPErr):
                raise
            raise HTTPErr(f"HTTP Request failed: {e}")

    @typed
    def get(url: Url('http', 'https'), data: Maybe(Data) = None, headers: Maybe(Union(Header, Dict)) = None, follow: Bool = True, timeout: Num = 11, params: Maybe(Dict)=None) -> Response:
        return await http.request("GET", url, data, headers, follow, timeout, params)

    @typed
    async def post(url: Url('http', 'https'), data: Maybe(Data) = None, headers: Maybe(Union(Header, Dict))=Header(type='json'), follow: Bool = True, timeout: Num = 10, params: Maybe(Dict) = None) -> Response:
        return await http.request("POST", url, data, headers, follow, timeout, params)

    @typed
    async def put(url: Url('http', 'https'), data: Maybe(Data)=None, headers: Maybe(Union(Header, Dict))=None, follow: Bool=True, timeout: Num=10, params: Maybe(Dict)=None) -> Response:
        return await http.request("PUT", url, data, headers, follow, timeout, params)

    @typed
    async def patch(url: Url('http', 'https'), data: Maybe(Data)=None, headers: Maybe(Union(Header, Dict))=None, follow: Bool = True, timeout: Num = 10, params: Maybe(Dict) = None) -> Response:
        return await http.request("PATCH", url, data, headers, follow, timeout, params)

    @typed
    async def delete(url: Url('http', 'https'), data: Maybe(Data)=None, headers: Maybe(Union(Header, Dict))=None, follow: Bool=True, timeout: Num=10, params: Maybe(Dict)=None) -> Response:
        return await http.request("DELETE", url, data, headers, follow, timeout, params)
