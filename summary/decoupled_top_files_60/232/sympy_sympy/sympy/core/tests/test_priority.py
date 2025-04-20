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
    """
    Test the multiplication behavior between different types of objects.
    
    This function checks the multiplication behavior between different types of objects, specifically focusing on the interaction between a symbol 'x', a 'Higher' object (h), and a 'Lower' object (l). The function evaluates the results of different multiplication operations and asserts the expected outcomes.
    
    Parameters:
    - None (The function uses predefined symbols and objects.)
    
    Returns:
    - None (The function asserts the expected results of the multiplication operations.)
    
    Key Points:
    - 'l
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l*h == h*l == 'high'
    assert x*h == h*x == 'high'
    assert l*x == x*l != 'low'


def test_add():
    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l + h == h + l == 'high'
    assert x + h == h + x == 'high'
    assert l + x == x + l != 'low'


def test_sub():
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
    """
    Tests the division operation between different symbolic and numeric entities.
    
    This function evaluates the division operation between various symbolic and numeric entities. It checks the division of a symbolic variable 'x' with 'Higher' and 'Lower' objects, and also the division of 'Higher' and 'Lower' objects with each other.
    
    Key Parameters:
    - x: A symbolic variable represented as a SymPy symbol.
    
    Returns:
    - None: This function does not return any value. It asserts the expected outcomes of the division operations
    """

    x = Symbol('x')
    h = Higher()
    l = Lower()
    assert l/h == h/l == 'high'
    assert x/h == h/x == 'high'
    assert l/x != 'low'
    assert x/l != 'low'
