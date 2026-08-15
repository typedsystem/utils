from typed import lazy

__imports__ = {
    "utils.mods.number.types": [
        "Num", "Nat", "Pos", "Neg", "Even", "Odd"
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
