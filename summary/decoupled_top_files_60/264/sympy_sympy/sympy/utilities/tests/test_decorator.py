from sympy.utilities.decorator import threaded, xthreaded, memoize_property

from sympy import Eq, Matrix, Basic

from sympy.abc import x, y
from sympy.core.decorators import wraps


def test_threaded():
    """
    Thread a function over a SymPy expression or object.
    
    This function takes a SymPy expression or object and applies a given function
    to it in a threaded manner. The function can be applied to matrices, equations,
    lists, tuples, and sets. The function can also be applied to a SymPy expression
    with an additional parameter, such as exponentiation.
    
    Parameters:
    expr (SymPy expression or object): The SymPy expression or object to be threaded over.
    *args: Additional arguments
    """

    @threaded
    def function(expr, *args):
        return 2*expr + sum(args)

    assert function(Matrix([[x, y], [1, x]]), 1, 2) == \
        Matrix([[2*x + 3, 2*y + 3], [5, 2*x + 3]])

    assert function(Eq(x, y), 1, 2) == Eq(2*x + 3, 2*y + 3)

    assert function([x, y], 1, 2) == [2*x + 3, 2*y + 3]
    assert function((x, y), 1, 2) == (2*x + 3, 2*y + 3)

    assert function({x, y}, 1, 2) == {2*x + 3, 2*y + 3}

    @threaded
    def function(expr, n):
        return expr**n

    assert function(x + y, 2) == x**2 + y**2
    assert function(x, 2) == x**2


def test_xthreaded():
    """
    Test a function that uses xthreaded decorator to raise an expression to a power.
    
    This function takes an expression and a power as input and returns the expression raised to the specified power.
    
    Parameters:
    expr (expression): The mathematical expression to be raised to a power.
    n (int): The power to which the expression is raised.
    
    Returns:
    expression: The result of raising the input expression to the specified power.
    
    Example:
    >>> function(x + y, 2)
    (x + y)**2
    """

    @xthreaded
    def function(expr, n):
        return expr**n

    assert function(x + y, 2) == (x + y)**2


def test_wraps():
    def my_func(x):
        """My function. """

    my_func.is_my_func = True

    new_my_func = threaded(my_func)
    new_my_func = wraps(my_func)(new_my_func)

    assert new_my_func.__name__ == 'my_func'
    assert new_my_func.__doc__ == 'My function. '
    assert hasattr(new_my_func, 'is_my_func')
    assert new_my_func.is_my_func is True


def test_memoize_property():
    """
    Test memoization of a property in a class.
    
    This function checks if the memoize_property decorator correctly caches the result of the 'prop' method. The 'prop' method returns an instance of the Basic class. The function creates an instance of TestMemoize, accesses the 'prop' property twice, and verifies that both accesses return the same instance.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The two instances returned by accessing the 'prop' property twice should be the same.
    
    Example
    """

    class TestMemoize(Basic):
        @memoize_property
        def prop(self):
            return Basic()

    member = TestMemoize()
    obj1 = member.prop
    obj2 = member.prop
    assert obj1 is obj2
