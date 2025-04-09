from sympy.core import Eq, Rational, Symbol
from sympy.functions import sin, cos, tan, csc, sec, cot, log, Piecewise
from sympy.integrals.trigonometry import trigintegrate

x = Symbol('x')


def test_trigintegrate_odd():
    """
    Integrates trigonometric functions.
    
    This function performs integration of various trigonometric functions
    with respect to the variable `x`. It handles basic integrals like
    integrating powers of `x` and trigonometric functions such as sine and
    cosine. For more complex cases involving products of sine and cosine,
    it uses piecewise expressions to handle different conditions. The
    function also supports symbolic integration with respect to a symbol
    `y`, and can simplify
    """

    assert trigintegrate(Rational(1), x) == x
    assert trigintegrate(x, x) is None
    assert trigintegrate(x**2, x) is None

    assert trigintegrate(sin(x), x) == -cos(x)
    assert trigintegrate(cos(x), x) == sin(x)

    assert trigintegrate(sin(3*x), x) == -cos(3*x)/3
    assert trigintegrate(cos(3*x), x) == sin(3*x)/3

    y = Symbol('y')
    assert trigintegrate(sin(y*x), x) == \
        Piecewise((0, Eq(y, 0)), (-cos(y*x)/y, True))
    assert trigintegrate(cos(y*x), x) == \
        Piecewise((x, Eq(y, 0)), (sin(y*x)/y, True))
    assert trigintegrate(sin(y*x)**2, x) == \
        Piecewise((0, Eq(y, 0)), ((x*y/2 - sin(x*y)*cos(x*y)/2)/y, True))
    assert trigintegrate(sin(y*x)*cos(y*x), x) == \
        Piecewise((0, Eq(y, 0)), (sin(x*y)**2/(2*y), True))
    assert trigintegrate(cos(y*x)**2, x) == \
        Piecewise((x, Eq(y, 0)), ((x*y/2 + sin(x*y)*cos(x*y)/2)/y, True))

    y = Symbol('y', positive=True)
    # TODO: remove conds='none' below. For this to work we would have to rule
    #       out (e.g. by trying solve) the condition y = 0, incompatible with
    #       y.is_positive being True.
    assert trigintegrate(sin(y*x), x, conds='none') == -cos(y*x)/y
    assert trigintegrate(cos(y*x), x, conds='none') == sin(y*x)/y

    assert trigintegrate(sin(x)*cos(x), x) == sin(x)**2/2
    assert trigintegrate(sin(x)*cos(x)**2, x) == -cos(x)**3/3
    assert trigintegrate(sin(x)**2*cos(x), x) == sin(x)**3/3

    # check if it selects right function to substitute,
    # so the result is kept simple
    assert trigintegrate(sin(x)**7 * cos(x), x) == sin(x)**8/8
    assert trigintegrate(sin(x) * cos(x)**7, x) == -cos(x)**8/8

    assert trigintegrate(sin(x)**7 * cos(x)**3, x) == \
        -sin(x)**10/10 + sin(x)**8/8
    assert trigintegrate(sin(x)**3 * cos(x)**7, x) == \
        cos(x)**10/10 - cos(x)**8/8


def test_trigintegrate_even():
    """
    Integrates trigonometric functions.
    
    Args:
    func (str): The trigonometric function to integrate.
    
    Returns:
    str: The integral of the given trigonometric function.
    """

    assert trigintegrate(sin(x)**2, x) == x/2 - cos(x)*sin(x)/2
    assert trigintegrate(cos(x)**2, x) == x/2 + cos(x)*sin(x)/2

    assert trigintegrate(sin(3*x)**2, x) == x/2 - cos(3*x)*sin(3*x)/6
    assert trigintegrate(cos(3*x)**2, x) == x/2 + cos(3*x)*sin(3*x)/6
    assert trigintegrate(sin(x)**2 * cos(x)**2, x) == \
        x/8 - sin(2*x)*cos(2*x)/16

    assert trigintegrate(sin(x)**4 * cos(x)**2, x) == \
        x/16 - sin(x) *cos(x)/16 - sin(x)**3*cos(x)/24 + \
        sin(x)**5*cos(x)/6

    assert trigintegrate(sin(x)**2 * cos(x)**4, x) == \
        x/16 + cos(x) *sin(x)/16 + cos(x)**3*sin(x)/24 - \
        cos(x)**5*sin(x)/6

    assert trigintegrate(sin(x)**(-4), x) == -2*cos(x)/(3*sin(x)) \
        - cos(x)/(3*sin(x)**3)

    assert trigintegrate(cos(x)**(-6), x) == sin(x)/(5*cos(x)**5) \
        + 4*sin(x)/(15*cos(x)**3) + 8*sin(x)/(15*cos(x))


def test_trigintegrate_mixed():
    """
    Integrates trigonometric expressions involving mixed functions.
    
    Args:
    expr (str): The trigonometric expression to integrate, specified as a string.
    
    Returns:
    str: The integrated result of the given trigonometric expression, expressed as a string.
    
    Examples:
    >>> trigintegrate('sin(x)*sec(x)')
    '-log(sin(x)**2 - 1)/2'
    >>> trigintegrate('cos(x)*sec(x)')
    'x'
    """

    assert trigintegrate(sin(x)*sec(x), x) == -log(sin(x)**2 - 1)/2
    assert trigintegrate(sin(x)*csc(x), x) == x
    assert trigintegrate(sin(x)*cot(x), x) == sin(x)

    assert trigintegrate(cos(x)*sec(x), x) == x
    assert trigintegrate(cos(x)*csc(x), x) == log(cos(x)**2 - 1)/2
    assert trigintegrate(cos(x)*tan(x), x) == -cos(x)
    assert trigintegrate(cos(x)*cot(x), x) == log(cos(x) - 1)/2 \
        - log(cos(x) + 1)/2 + cos(x)


def test_trigintegrate_symbolic():
    """
    Test symbolic integration of trigonometric functions.
    
    This function checks if the symbolic integration of various trigonometric
    functions with respect to 'x' can be performed when the power 'n' is an
    integer. The functions tested include cosine raised to the power 'n',
    sine raised to the power 'n', and cotangent raised to the power 'n'.
    
    Parameters:
    None
    
    Returns:
    None: The function asserts whether the integration results are None,
    """

    n = Symbol('n', integer=True)
    assert trigintegrate(cos(x)**n, x) is None
    assert trigintegrate(sin(x)**n, x) is None
    assert trigintegrate(cot(x)**n, x) is None
