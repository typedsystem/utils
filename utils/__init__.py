from typed import lazy

__imports__ = {
    "utils.mods.checker": [
        "check", "require"
    ],
    "utils.mods.types": [
        "Regex", "Enum", "Value", "Null", "Maybe"
    ]
}

if lazy(__imports__):
    from utils.mods.checker import (
        check, require
    )
    from utils.mods.types import (
        Regex, Enum, Value, Null, Maybe 
    )
