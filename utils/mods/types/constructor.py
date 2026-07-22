from typed import Filtered, typed, Tuple, Any, Str
from typed.meta import TYPE

@typed
def Regex(regex: Str) -> TYPE:
    import re
    filter = lambda x: re.compile(regex).match(x) is not None

    rgx = Filtered(
        Str,
        filters=(filter,)
    )
    rgx.__name__ = f"Regex({regex})"
    rgx.__display__ = rgx.__name__

    return rgx

@typed
def Enum(*values: Tuple) -> TYPE:
    from typed import Filtered, Union, prop, Any

    base_type = Union(
        *(prop.typeof(val) for val in values),
        base=Any
    )
    filter = lambda x: x in values

    enum = Filtered(
        base_type,
        filters=(filter,)
    )
    enum.__name__ = f"Enum({prop.nameof(values)})"
    enum.__display__ = enum.__name__
    enum.__values__ = values

    return enum

@typed
def Value(val: Any) -> TYPE:
    value = Enum(val)
    value.__name__ = f"Value({val})"
    value.__display__ = value.__name__

    return value

@typed
def Maybe(*types: Tuple(TYPE)) -> TYPE:
    from typed import Union, Nill, prop

    maybe = Union(*types, Nill)
    maybe.__name__ = f"Maybe({prop.nameof(types)})"
    maybe.__display__ = maybe.__name__

    return maybe
