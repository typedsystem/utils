from typed import Enriched
from utils.mods.path.service import (
    PathService,
    ExistsService,
    FileService,
    DirService,
    MountService,
    SymlinkService,
    CompressedService
)
from utils.mods.path.types import (
    Path as PathType,
    Exists as ExistsType,
    File as FileType,
    Dir as DirType,
    Mount as MountType,
    Symlink as SymlinkType,
    Compressed as CompressedType
)

Path       = Enriched(PathType, service=PathService)
Exists     = Enriched(ExistsType, service=ExistsService)
File       = Enriched(FileType, service=FileService)
Dir        = Enriched(DirType, service=DirService)
Mount      = Enriched(MountType, service=MountService)
Symlink    = Enriched(SymlinkType, service=SymlinkService)
Compressed = Enriched(CompressedType, service=CompressedService)
