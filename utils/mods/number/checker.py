from typed.checker import Checker

class NumberChecker(Checker):
    def isnum(self, entity: object) -> bool:
        from utils.mods.number.types import Num
        return entity in Num

    def isint(self, entity: object) -> bool: 
        from typed import Int
        return entity in Int

    def isfloat(self, entity: object) -> bool:
        from typed import Float
        return entity in Float

    def isnat(self, entity: object) -> bool:
        from utils.mods.number.types import Nat
        return entity in Nat

    def ispos(self, entity: object) -> bool:
        from utils.mods.number.types import Pos
        return entity in Pos

    def isneg(self, entity: object) -> bool:
        from utils.mods.number.types import Neg
        return entity in Neg

    def iseven(self, entity: object) -> bool:
        from utils.mods.number.types import Even
        return entity in Even

    def isodd(self, entity: object) -> bool:
        from utils.mods.number.types import Odd
        return entity in Odd

number_require = NumberChecker(quantifier=None, explode=True)
number_check = NumberChecker(quantifier=None, explode=False)
