from typed import Union, Str, Filtered, Regex, Null, prop
from typed.meta import TYPE
from typed.wrap import family
from utils.helper.path import (
    _exists,
    _is_file,
    _is_dir,
    _is_mount,
    _is_symlink,
    _is_compressed,
    _has_encoding,
    _has_mime
)

Path = Union(Regex(r"^/?(?:(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?|/?)$"), Null(Str))

Exists     = Filtered(Path, _exists)
File       = Filtered(Path, _is_file)
Dir        = Filtered(Path, _is_dir)
Symlink    = Filtered(Path, _is_symlink)
Mount      = Filtered(Dir, _is_mount)
Compressed = Filtered(File, _is_compressed)

@family
def Encoded(encoding: Str) -> TYPE:
    encoded = Filtered(Exists, _has_encoding(..., encoding=encoding))
    prop.set.nameof(encoded, f"Encoded({encoding})")
    return encoded

@family
def Mime(mime: Str) -> TYPE:
    mimed = Filtered(Exists, _has_mime(..., mime=mime))
    prop.set.nameof(mimed, f"Mime({mime})")
    return mimed

prop.set.nameof(Path,      "Path")
prop.set.nameof(Exists,    "Exists")
prop.set.nameof(File,      "File")
prop.set.nameof(Dir,       "Dir")
prop.set.nameof(Symlink,   "Symlink")
prop.set.nameof(Mount,     "Mount")

prop.set.nullof(Path,      "")
prop.set.nullof(Exists,    Path.__null__)
prop.set.nullof(File,      Path.__null__)
prop.set.nullof(Dir,       Path.__null__)
prop.set.nullof(Symlink,   Path.__null__)
prop.set.nullof(Mount,     Path.__null__)
