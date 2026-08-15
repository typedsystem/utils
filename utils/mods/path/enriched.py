from typed.mods.types.service import Enriched
from utils.mods.path.service import path, exists, file, dir, mount, symlink
from utils.mods.path.types import (
    Path as PathType,
    Exists as ExistsType,
    File as FileType,
    Dir as DirType,
    Mount as MountType,
    Symlink as SymlinkType
)

Path    = Enriched(PathType, service=path)
Exists  = Enriched(ExistsType, service=exists)
File    = Enriched(FileType, service=file)
Dir     = Enriched(DirType, service=dir)
Mount   = Enriched(MountType, service=mount)
Symlink = Enriched(SymlinkType, service=symlink)
