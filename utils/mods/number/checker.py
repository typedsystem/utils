from typed.checker import Checker

class NumberChecker(Checker):
    def isnum(self, entity: object) -> bool:
        from utils.mods.number.types import Num
        if self.explode:
            from typed import require
            require.isterm(entity, Num)
        from typed import check
        return check.isterm(entity, Num)

    def isint(self, entity: object) -> bool: 
        from typed import Int
        if self.explode:
            from typed import require
            require.isterm(entity, Int)
        from typed import check
        return check.isterm(entity, Int)

    def isfloat(self, entity: object) -> bool:
        from typed import Float
        if self.explode:
            from typed import require
            require.isterm(entity, Float)
        from typed import check
        return check.isterm(entity, Float)

    def isnat(self, entity: object) -> bool:
        from utils.mods.number.types import Nat
        if self.explode:
            from typed import require
            require.isterm(entity, Nat)
        from typed import check
        return check.isterm(entity, Nat)

    def ispos(self, entity: object) -> bool:
        from utils.mods.number.types import Pos
        if self.explode:
            from typed import require
            require.isterm(entity, Pos)
        from typed import check
        return check.isterm(entity, Pos)

    def isneg(self, entity: object) -> bool:
        from utils.mods.number.types import Neg
        if self.explode:
            from typed import require
            require.isterm(entity, Neg)
        from typed import check
        return check.isterm(entity, Neg)

    def iseven(self, entity: object) -> bool:
        from utils.mods.number.types import Even
        if self.explode:
            from typed import require
            require.isterm(entity, Even)
        from typed import check
        return check.isterm(entity, Even)

    def isodd(self, entity: object) -> bool:
        from utils.mods.number.types import Odd
        if self.explode:
            from typed import require
            require.isterm(entity, Odd)
        from typed import check
        return check.isterm(entity, Odd)

number_require = NumberChecker(quantifier=None, explode=True)
number_check = NumberChecker(quantifier=None, explode=False)
