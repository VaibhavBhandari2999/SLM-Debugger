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
    Test multiplication behavior for different types of objects.
    
    This function evaluates the multiplication behavior between different types of objects, specifically focusing on the interaction between a symbolic variable 'x', a 'Higher' object, and a 'Lower' object. The function checks the commutativity of multiplication and the resulting type of the product.
    
    Parameters:
    - x (Symbol): A symbolic variable.
    
    Returns:
    - None: The function does not return any value. It asserts the expected behavior of multiplication.
    
    Key Points:
    - The
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
    """
    Test the power operation between different levels (low and high) and a symbol.
    
    This function evaluates the power operation between different symbolic and literal
    inputs. It checks the interaction between a symbolic variable 'x', and the literal
    values 'low' and 'high'.
    
    Parameters:
    - x (Symbol): A symbolic variable representing a generic value.
    
    Returns:
    - None: The function asserts the results of the power operations and does not return any value.
    
    Key Assertions:
    - l**h and h**l
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
