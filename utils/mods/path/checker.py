from typed.checker import Checker

class PathChecker(Checker):
    def ispath(self, path: str) -> bool:
        from utils.mods.path.types import Path
        return path in Path

    def exists(self, path: str) -> bool:
        from utils.mods.path.types import Exists
        return path in Exists

    def isfile(self, path: str) -> bool:
        from utils.mods.path.types import File
        return path in File

    def isdir(self, path: str) -> bool:
        from utils.mods.path.types import Dir
        return path in Dir

    def ismount(self, path: str) -> bool:
        from utils.mods.path.types import Mount
        return path in Mount

    def issymlink(self, path: str) -> bool:
        from utils.mods.path.types import Symlink
        return path in Symlink

path_require = PathChecker(quantifier=None, explode=True)
path_check = PathChecker(quantifier=None, explode=False)

