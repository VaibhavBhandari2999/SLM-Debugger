from sympy.utilities.decorator import threaded, xthreaded, memoize_property

from sympy import Eq, Matrix, Basic

from sympy.abc import x, y
from sympy.core.decorators import wraps


def test_threaded():
    """
    Thread a function over an expression or collection.
    
    This function takes a function and applies it to each element of an expression or collection in a threaded manner. It supports various input types such as matrices, equations, lists, and tuples. The function can also handle nested collections and apply the threaded operation recursively.
    
    Parameters:
    function (callable): The function to be threaded over the input expression or collection.
    expr (expression or collection): The input expression or collection to which the function will be applied.
    
    Returns
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
    
    This function creates a class `TestMemoize` that inherits from `Basic`. It defines a property `prop` using the `@memoize_property` decorator. The `prop` property returns an instance of `Basic`. The function checks if the property is memoized correctly, meaning that calling `prop` multiple times returns the same instance.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Notes:
    - The function asserts that the two calls
    """

    class TestMemoize(Basic):
        @memoize_property
        def prop(self):
            return Basic()

    member = TestMemoize()
    obj1 = member.prop
    obj2 = member.prop
    assert obj1 is obj2
