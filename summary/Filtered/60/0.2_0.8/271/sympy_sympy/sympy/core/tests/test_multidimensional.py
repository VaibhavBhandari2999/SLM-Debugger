from sympy import diff, sin, symbols, Function, Derivative
from sympy.core.multidimensional import vectorize
x, y, z = symbols('x y z')
f, g, h = list(map(Function, 'fgh'))


def test_vectorize():
    """
    Vectorize a function or operation.
    
    Parameters:
    0 (int): Indicates that the function should be vectorized over the first argument.
    1 (int): Indicates that the function should be vectorized over the second argument.
    
    Returns:
    Function: A vectorized version of the input function or operation.
    
    Examples:
    >>> @vectorize(0)
    ... def vsin(x):
    ...     return sin(x)
    >>> vsin([1, x, y])
    [
    """

    @vectorize(0)
    def vsin(x):
        return sin(x)

    assert vsin([1, x, y]) == [sin(1), sin(x), sin(y)]

    @vectorize(0, 1)
    def vdiff(f, y):
        return diff(f, y)

    assert vdiff([f(x, y, z), g(x, y, z), h(x, y, z)], [x, y, z]) == \
         [[Derivative(f(x, y, z), x), Derivative(f(x, y, z), y),
           Derivative(f(x, y, z), z)], [Derivative(g(x, y, z), x),
                     Derivative(g(x, y, z), y), Derivative(g(x, y, z), z)],
         [Derivative(h(x, y, z), x), Derivative(h(x, y, z), y), Derivative(h(x, y, z), z)]]
