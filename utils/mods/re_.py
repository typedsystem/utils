from typed.mods.meta.base import STR
from typed.mods.types.base import Str

class PATTERN(STR):
    def __term__(typ, trm):
        import re
        from typed.mods.core import term
        if not term(trm, Str):
            return False
        try:
            re.compile(trm)
            return True
        except re.error:
            return False

Pattern = PATTERN("Pattern", (Str,), {"__display__": "Pattern", "__null__": ""})
