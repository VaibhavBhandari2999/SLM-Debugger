from sympy import Expr, Symbol
from sympy.core.decorators import call_highest_priority


class Higher(Expr):

    _op_priority = 20.0
    result = 'high'

    @call_highest_priority('__rmul__')
    def __mul__(self, other):
        return self.result

    @call_highest_priority('__mul__')
    def __rmul__(self, other):
        return self.result

    @call_highest_priority('__radd__')
    def __add__(self, other):
        return self.result

    @call_highest_priority('__add__')
    def __radd__(self, other):
        return self.result

    @call_highest_priority('__rsub__')
    def __sub__(self, other):
        return self.result

    @call_highest_priority('__sub__')
    def __rsub__(self, other):
        return self.result

    @call_highest_priority('__rpow__')
    def __pow__(self, other):
        return self.result

    @call_highest_priority('__pow__')
    def __rpow__(self, other):
        return self.result

    @call_highest_priority('__rdiv__')
    def __div__(self, other):
        return self.result

    @call_highest_priority('__div__')
    def __rdiv__(self, other):
        return self.result

    __truediv__ = __div__
    __rtruediv__ = __rdiv__


class Lower(Higher):

    _op_priority = 5.0
    result = 'low'


def test_mul():
    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l*h == h*l == 'high'
    assert x*h == h*x == 'high'
    assert l*x == x*l != 'low'


def test_add():
    """
    Test the addition operation between different types of objects.
    
    This function tests the addition operation between a symbolic variable 'x', a 'Higher' object, and a 'Lower' object. It checks the commutative property of addition and the outcome of adding different types of objects.
    
    Parameters:
    x (Symbol): A symbolic variable.
    
    Returns:
    str: The result of the addition operation.
    
    Key Points:
    - 'Lower' + 'Higher' and 'Higher' + 'Lower' both result in 'high
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l + h == h + l == 'high'
    assert x + h == h + x == 'high'
    assert l + x == x + l != 'low'


def test_sub():
    """
    Subtract two values or expressions.
    
    This function subtracts two values or expressions, handling symbolic and
    higher/lower value comparisons.
    
    Parameters:
    x (Symbol): A symbolic variable.
    h (Higher): An object representing a higher value.
    l (Lower): An object representing a lower value.
    
    Returns:
    str: The result of the subtraction, which can be a string indicating
    the relative values ('high', 'low', or 'x - h' for symbolic expressions).
    
    Examples
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l - h == h - l == 'high'
    assert x - h == h - x == 'high'
    assert l - x == -(x - l) != 'low'


def test_pow():
    """
    Test the power operation between different levels (low, high, and symbol).
    
    This function evaluates the power operation between different symbolic levels and
    numeric symbols. It checks the behavior of the power operation when the base is
    either a symbolic level or a symbol, and the exponent is a symbolic level.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - l**h and h**l are both evaluated to 'high'.
    - x**h and h**x are both evaluated
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l**h == h**l == 'high'
    assert x**h == h**x == 'high'
    assert l**x != 'low'
    assert x**l != 'low'


def test_div():
    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l/h == h/l == 'high'
    assert x/h == h/x == 'high'
    assert l/x != 'low'
    assert x/l != 'low'
