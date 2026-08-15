from typed import lazy

__imports__ = {
    "utils.mods.path.types": [
        "Encoded", "Mime"
    ],
    "utils.mods.path.enriched": [
        "Path", "Exists",
        "File", "Dir",
        "Mount", "Symlink",
        "Compressed"
    ],
    "utils.mods.path.err": [
        "PathErr", "ExistsErr",
        "FileErr", "DirErr",
        "MountErr", "SymlinkErr",
        "CompressedErsr"
    ]    
}

if lazy(__imports__):
    from utils.mods.path.types import (
        Encoded, Mime        
    )
    from utils.mods.path.enriched import (
        Path, Exists,
        File, Dir,
        Mount, Symlink, Compressed
    )
    from utils.mods.path.err import (
        PathErr, ExistsErr,
        FileErr, DirErr,
        MountErr, SymlinkErr,
        CompressedErr
    )
