from typed import lazy

__imports__ = {
    "utils.mods.checker": [
        "check", "require"
    ]
}

if lazy(__imports__):
    from utils.mods.checker import (
        check, require
    )
