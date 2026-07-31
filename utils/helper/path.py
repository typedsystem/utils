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
