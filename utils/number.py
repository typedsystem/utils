from typed import lazy

__imports__ = {
    "utils.mods.number.types": [
        "path", "exists", "file", "dir", "mount", "symlink"
    ],
    "utils.mods.number.err": [
        "NumberErr"
    ],
}

if lazy(__imports__):
    from utils.mods.number.types import (
        Num, Nat, Pos, Neg, Even, Odd
    )
    from utils.mods.number.err import NumberErr
