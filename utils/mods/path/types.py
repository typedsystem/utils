from typed import Union, Str, Filtered, prop
from utils.mods.types import Regex, Null, Enum
from utils.helper.path import (
    _exists,
    _is_file,
    _is_dir,
    _is_mount,
    _is_symlink
)

Path = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))

Exists  = Filtered(Path, _exists)
File    = Filtered(Path, _is_file)
Dir     = Filtered(Path, _is_dir)
Symlink = Filtered(Path, _is_symlink)
Mount   = Filtered(Path, _is_mount)

PathKinds = Enum(File, Dir, Symlink, Mount)

prop.set.nameof(Path,      "Path")
prop.set.nameof(Exists,    "Exists")
prop.set.nameof(File,      "File")
prop.set.nameof(Dir,       "Dir")
prop.set.nameof(Symlink,   "Symlink")
prop.set.nameof(Mount,     "Mount")
prop.set.nameof(PathKinds, "PathKinds")

prop.set.nullof(Path,      "")
prop.set.nullof(Exists,    Path.__null__)
prop.set.nullof(File,      Path.__null__)
prop.set.nullof(Dir,       Path.__null__)
prop.set.nullof(Symlink,   Path.__null__)
prop.set.nullof(Mount,     Path.__null__)
prop.set.nullof(PathKinds, Path.__null__)
