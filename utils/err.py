from typed import lazy

__imports__ = {
    "utils.mods.err": [
        "NotDefined",
        "NotExists",
        "NotConnected",
        "NotFound",
        "NotMatch",
        "NotRegistered",
        "NotSet",
        "AlreadyDefined",
        "AlreadyExists",
        "AlreadyRegistered",
        "AlreadyConnected",
        "AlreadySet"
    ]
}

if lazy(__imports__):
    from utils.mods.err import (
        NotDefined,
        NotExists,
        NotConnected,
        NotFound,
        NotMatch,
        NotRegistered,
        NotSet,
        AlreadyDefined,
        AlreadyExists,
        AlreadyRegistered,
        AlreadyConnected,
        AlreadySet
    )

