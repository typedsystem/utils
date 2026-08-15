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
