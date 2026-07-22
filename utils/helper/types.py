from functools import lru_cache as cache
from typed import Len, Regex, Str, Union, null, TYPE
from utils.mods.path import Path
from utils.mods.url import Url

Char    = Len(Str, 1)
Email   = Regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PathUrl = Union(Path, Url)
UUID    = Regex(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

Char.__display__    = "Char"
Email.__display__   = "Email"
PathUrl.__display__ = "PathUrl"
UUID.__display__    = "UUID"

PathUrl.__null__ = ""

@cache
def Extension(*exts):
    class EXTENSION(TYPE(PathUrl)):
        def __instancecheck__(cls, instance):
            if not isinstance(instance, PathUrl):
                return False
            if instance == '':
                return True
            parts = instance.split('.')
            return any(parts[-1] == ext for ext in exts)
    class_name = f"Extension({', '.join(exts)})"
    return EXTENSION(class_name, (PathUrl,), {
        "__display__": class_name,
        "__null__": null(PathUrl)
    })
