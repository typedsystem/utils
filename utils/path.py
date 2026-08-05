from typed import lazy

__imports__ = {
    "utils.mods.path.service": [
        "path", "exists",
        "file", "dir",
        "mount", "symlink"
    ],
    "utils.mods.path.enriched": [
        "Path", "Exists",
        "File", "Dir",
        "Mount", "Symlink"
    ],
    "utils.mods.path.err": [
        "PathErr", "ExistsErr",
        "FileErr", "DirErr",
        "MountErr", "SymlinkErr"
    ]    
}

if lazy(__imports__):
    from utils.mods.path.service import (
        path, exists,
        file, dir,
        mount, symlink
    )
    from utils.mods.path.enriched import (
        Path, Exists,
        File, Dir,
        Mount, Symlink
    )
    from utils.mods.path.err import (
        PathErr, ExistsErr,
        FileErr, DirErr,
        MountErr, SymlinkErr
    )
