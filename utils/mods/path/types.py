from typed import Union, Str, Filtered, prop
from utils.mods.types import Regex, Null
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

prop.set.nameof(Path,    "Path")
prop.set.nameof(Exists,  "Exists")
prop.set.nameof(File,    "File")
prop.set.nameof(Dir,     "Dir")
prop.set.nameof(Symlink, "Symlink")
prop.set.nameof(Mount,   "Mount")

Path.__null__    = ""
Exists.__null__  = Path.__null__
File.__null__    = Path.__null__
Dir.__null__     = Path.__null__
Symlink.__null__ = Path.__null__
Mount.__null__   = Path.__null__
