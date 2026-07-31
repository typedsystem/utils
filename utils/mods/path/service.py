from typed import service, action, term
from utils.mods.path.types import Path

@service
class path:
    @action
    def cwd(trm) -> Path:
        import os
        return term(os.path.curdir())

    @action
    def here(trm) -> Path:
        import os
        return term(os.path.dirname(__file__))
