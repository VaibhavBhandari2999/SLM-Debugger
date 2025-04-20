from sympy import diff, sin, symbols, Function, Derivative
from sympy.core.multidimensional import vectorize
x, y, z = symbols('x y z')
f, g, h = list(map(Function, 'fgh'))


def test_vectorize():
    """
    Vectorize a function or operation over a list or tuple of arguments.
    
    Parameters:
    - func: The function to be vectorized. It can be a single function or a tuple of functions.
    - args: A list or tuple of arguments over which the function should be applied.
    
    Returns:
    - A list or tuple containing the results of applying the function to each argument.
    
    Example:
    - vsin([1, x, y]) will return [sin(1), sin(x), sin(y)].
    -
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
