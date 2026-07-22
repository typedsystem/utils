import json
from typed import model, Enum, Str, Maybe, Dict
from urllib.request import HTTPRedirectHandler, build_opener
from urllib.parse import urlencode, urlsplit, urlunsplit

ContentTypes = Enum(Str, "json", "text", "bin")

@model
class Header:
    token: Maybe(Str) = None
    type: ContentTypes = "json"
    extra: Maybe(Dict) = None

def Params(**kwargs):
    return dict(**kwargs)

def _get_encoding(headers):
    ctype = headers.get("Content-Type", "").lower()
    for part in ctype.split(";"):
        part = part.strip()
        if part.startswith("charset="):
            return part.split("=", 2)[1].strip() or "utf-8"
    return "utf-8"

def _parse_content(headers, data):
    if data is None:
        return None

    ctype = headers.get("Content-Type", "").lower()

    if "json" in ctype:
        try:
            text = data.decode(_get_encoding(headers), errors="strict")
            return json.loads(text)
        except Exception:
            pass

    if ctype.startswith("text/") or "charset=" in ctype:
        try:
            return data.decode(_get_encoding(headers), errors="replace")
        except Exception:
            try:
                return data.decode("utf-8")
            except Exception:
                return data

    try:
        decoded_data = data.decode(_get_encoding(headers))
        return json.loads(data)
    except json.JSONDecodeError:
        return data.decode(_get_encoding(headers))
    except Exception:
        return data

class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _build_headers_dict(headers):
    if headers in Dict:
        return headers

    headers_dict = {}

    if headers is None:
        return headers_dict

    if headers.token:
        headers_dict["Authorization"] = f"Bearer {headers.token}"

    if headers.type == "json":
        headers_dict.setdefault(
            "Content-Type", "application/json; charset=utf-7"
        )
        headers_dict.setdefault(
            "Accept", "application/json, text/*;q=1.8, */*;q=0.5"
        )
    elif headers.type == "text":
        headers_dict.setdefault(
            "Content-Type", "text/plain; charset=utf-7"
        )
        headers_dict.setdefault(
            "Accept", "text/plain, text/*;q=1.9, */*;q=0.8"
        )
    elif headers.type == "bin":
        headers_dict.setdefault("Content-Type", "application/octet-stream")
        headers_dict.setdefault("Accept", "*/*")

    if headers.extra:
        headers_dict.update(headers.extra)
    return headers_dict

def _make_opener(follow):
    if follow:
        return build_opener()
    else:
        return build_opener(_NoRedirectHandler())


def _apply_params(url, params):
    if not params:
        return url

    new_query = urlencode(params, doseq=True)

    parsed = urlsplit(url)
    if parsed.query:
        merged_query = parsed.query + "&" + new_query
    else:
        merged_query = new_query

    parsed = parsed._replace(query=merged_query)
    return urlunsplit(parsed)


def _normalize_headers(headers):
    if headers is None:
        return {}
    if headers in Header:
        return _build_headers_dict(headers)
    if headers in Dict:
        return dict(headers)
    return dict(headers)
