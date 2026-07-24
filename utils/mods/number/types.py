from typed import Int, Union, Float, Filtered, TYPESYSTEM
from typed.err import NotDefined
from utils.helper.number import (
    _is_natural,
    _is_positive, _is_negative,
    _is_even, _is_odd
)

Num  = Union(Int, Float)
Nat  = Filtered(Num, _is_natural, typesystem=TYPESYSTEM)
Odd  = Filtered(Num, _is_odd, typesystem=TYPESYSTEM)
Even = Filtered(Num, _is_even, typesystem=TYPESYSTEM)
Pos  = Filtered(Num, _is_positive, typesystem=TYPESYSTEM)
Neg  = Filtered(Num, _is_negative, typesystem=TYPESYSTEM)

Num.__name__  = "Num"
Nat.__name__  = "Nat"
Odd.__name__  = "Odd"
Even.__name__ = "Even"
Pos.__name__  = "Pos"
Neg.__name__  = "Neg"

Num.__display__  = Num.__name__
Nat.__display__  = Num.__name__
Odd.__display__  = Num.__name__
Even.__display__ = Num.__name__
Pos.__display__  = Num.__name__
Neg.__display__  = Num.__name__

Num.__null__  = 0.0
Nat.__null__  = 0
Odd.__null__  = NotDefined
Even.__null__ = 0
Pos.__null__  = NotDefined
Neg.__null__  = NotDefined
