from typed import Int, Union, Float, Filtered, prop
from typed.err import NotDefined
from utils.helper.number import (
    _is_natural,
    _is_positive, _is_negative,
    _is_even, _is_odd
)

Num  = Union(Int, Float)
Nat  = Filtered(Num, _is_natural)
Odd  = Filtered(Num, _is_odd)
Even = Filtered(Num, _is_even)
Pos  = Filtered(Num, _is_positive)
Neg  = Filtered(Num, _is_negative)

prop.set.nameof(Num,  "Null")
prop.set.nameof(Nat,  "Nat")
prop.set.nameof(Odd,  "Odd")
prop.set.nameof(Even, "Even")
prop.set.nameof(Pos,  "Pos")
prop.set.nameof(Neg,  "Neg")

Num.__null__  = 0.0
Nat.__null__  = 0
Odd.__null__  = NotDefined
Even.__null__ = 0
Pos.__null__  = NotDefined
Neg.__null__  = NotDefined
