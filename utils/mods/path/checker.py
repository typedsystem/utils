from typed.checker import Checker

class PathChecker(Checker):
    def ispath(self, entity: str) -> bool:
        from utils.mods.path.types import Path
        if self.explode:
            from typed import require
            require.isterm(entity, Path)
        from typed import check
        return check.isterm(entity, Path)

    def exists(self, entity: str) -> bool:
        from utils.mods.path.types import Exists
        if self.explode:
            from typed import require
            require.isterm(entity, Exists)
        from typed import check
        return check.isterm(entity, Exists)

    def isfile(self, entity: str) -> bool:
        from utils.mods.path.types import File
        if self.explode:
            from typed import require
            require.isterm(entity, File)
        from typed import check
        return check.isterm(entity, File)

    def isdir(self, entity: str) -> bool:
        from utils.mods.path.types import Dir
        if self.explode:
            from typed import require
            require.isterm(entity, Dir)
        from typed import check
        return check.isterm(entity, Dir)

    def ismount(self, entity: str) -> bool:
        from utils.mods.path.types import Mount
        if self.explode:
            from typed import require
            require.isterm(entity, Mount)
        from typed import check
        return check.isterm(entity, Mount)

    def issymlink(self, entity: str) -> bool:
        from utils.mods.path.types import Symlink
        if self.explode:
            from typed import require
            require.isterm(entity, Symlink)
        from typed import check
        return check.isterm(entity, Symlink)

    def iscompressed(self, entity: str) -> bool:
        from utils.mods.path.types import Compressed
        if self.explode:
            from typed import require
            require.isterm(entity, Compressed)
        from typed import check
        return check.isterm(entity, Compressed)

path_require = PathChecker(quantifier=None, explode=True)
path_check = PathChecker(quantifier=None, explode=False)

