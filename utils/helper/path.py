from typed.func import func

def _exists(path: str) -> bool:
    import os
    return os.path.exists(path)

def _is_file(path: str) -> bool:
    import os
    return os.path.isfile(path)

def _is_dir(path: str) -> bool:
    import os
    return os.path.isdir(path)

def _is_symlink(path: str) -> bool:
    import os
    return os.path.islink(path)

def _is_mount(path: str) -> bool:
    import os
    return os.path.ismount(path)

@func
def _has_mime(path: str, mime: str) -> bool:
    import mimetypes
    mime_, _ = mimetypes.guess_type(path)
    return mime == mime_

@func
def _has_encoding(path: str, encoding: str) -> bool:
    import mimetypes
    _, encoding_ = mimetypes.guess_type(path)
    return encoding == encoding_

def _is_compressed(path: str, mime: str=None, encoding: str=None) -> bool:
    import os

    if not os.path.isfile(path):
        return False

    if mime is not None:
        compressed_mimes = (
            "application/zip",
            "application/x-tar",
            "application/gzip",
            "application/x-bzip2",
            "application/x-xz",
            "application/x-7z-compressed",
            "application/vnd.rar"
        )
        if mime in compressed_mimes:
            return True

    if encoding is not None:
        compressed_encodings = (
            "gzip",
            "bzip2",
            "xz",
            "compress"
        )
        if encoding in compressed_encodings:
            return True

    return False
