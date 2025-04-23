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
    
    This function tests the addition operation between a symbolic variable 'x', a 'Higher' object, and a 'Lower' object. It evaluates the results of adding these objects in different orders and combinations.
    
    Parameters:
    - x (Symbol): A symbolic variable.
    
    Returns:
    - str: The result of the addition operation.
    
    Key Points:
    - Adding 'Lower' and 'Higher' objects results in 'high'.
    - Adding 'Higher' and 'Lower'
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
    higher/lower value comparisons. It supports subtraction between a symbolic
    variable and a higher/lower value, as well as between two higher/lower values.
    
    Parameters:
    - x: A symbolic variable or a higher/lower value.
    - h: A higher value.
    - l: A lower value.
    
    Returns:
    - The result of the subtraction. If both inputs are higher/lower values,
    the
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l - h == h - l == 'high'
    assert x - h == h - x == 'high'
    assert l - x == -(x - l) != 'low'


def test_pow():
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
