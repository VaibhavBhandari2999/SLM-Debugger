from sympy.core import Ne, Rational, Symbol
from sympy.functions import sin, cos, tan, csc, sec, cot, log, Piecewise
from sympy.integrals.trigonometry import trigintegrate

x = Symbol('x')


def test_trigintegrate_odd():
    """
    Test the integration of trigonometric functions.
    
    This function tests the integration of various trigonometric functions and their combinations. It checks for the correct integration of basic functions, their multiples, and compositions with other functions. The function also handles symbolic integration with respect to a variable and includes conditions for positive symbols.
    
    Parameters:
    - func: The trigonometric function to integrate.
    - x: The variable of integration.
    
    Returns:
    - The integral of the trigonometric function with respect to the variable.
    -
    """

    assert trigintegrate(Rational(1), x) == x
    assert trigintegrate(x, x) is None
    assert trigintegrate(x**2, x) is None

    assert trigintegrate(sin(x), x) == -cos(x)
    assert trigintegrate(cos(x), x) == sin(x)

    assert trigintegrate(sin(3*x), x) == -cos(3*x)/3
    assert trigintegrate(cos(3*x), x) == sin(3*x)/3

    y = Symbol('y')
    assert trigintegrate(sin(y*x), x) == Piecewise(
        (-cos(y*x)/y, Ne(y, 0)), (0, True))
    assert trigintegrate(cos(y*x), x) == Piecewise(
        (sin(y*x)/y, Ne(y, 0)), (x, True))
    assert trigintegrate(sin(y*x)**2, x) == Piecewise(
        ((x*y/2 - sin(x*y)*cos(x*y)/2)/y, Ne(y, 0)), (0, True))
    assert trigintegrate(sin(y*x)*cos(y*x), x) == Piecewise(
        (sin(x*y)**2/(2*y), Ne(y, 0)), (0, True))
    assert trigintegrate(cos(y*x)**2, x) == Piecewise(
        ((x*y/2 + sin(x*y)*cos(x*y)/2)/y, Ne(y, 0)), (x, True))

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

    # both n, m are odd and -ve, and not necessarily equal
    assert trigintegrate(sin(x)**-1*cos(x)**-1, x) == \
        -log(sin(x)**2 - 1)/2 + log(sin(x))


def test_trigintegrate_even():
    """
    Test the integration of trigonometric functions.
    
    This function tests the integration of various trigonometric functions, including
    sine, cosine, and their combinations, with different exponents and arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Integrates functions like sin(x)**2, cos(x)**2, and their combinations.
    - Handles functions with different arguments, such as sin(3*x)**2 and cos(3*x)**2.
    - Tests integr
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
    assert trigintegrate(sin(x)*sec(x), x) == -log(cos(x))
    assert trigintegrate(sin(x)*csc(x), x) == x
    assert trigintegrate(sin(x)*cot(x), x) == sin(x)

    assert trigintegrate(cos(x)*sec(x), x) == x
    assert trigintegrate(cos(x)*csc(x), x) == log(sin(x))
    assert trigintegrate(cos(x)*tan(x), x) == -cos(x)
    assert trigintegrate(cos(x)*cot(x), x) == log(cos(x) - 1)/2 \
        - log(cos(x) + 1)/2 + cos(x)
    assert trigintegrate(cot(x)*cos(x)**2, x) == log(sin(x)) - sin(x)**2/2


def test_trigintegrate_symbolic():
    n = Symbol('n', integer=True)
    assert trigintegrate(cos(x)**n, x) is None
    assert trigintegrate(sin(x)**n, x) is None
    assert trigintegrate(cot(x)**n, x) is None
   with respect to the variable x. The integration is performed for functions
    involving powers of cosine, sine, and cotangent.
    
    Parameters:
    n (Symbol): An integer symbol representing the power to which the trigonometric
    functions are raised.
    
    Returns:
    None: The function returns None, as symbolic integration of these functions
    does not yield a specific result in the
    """

    n = Symbol('n', integer=True)
    assert trigintegrate(cos(x)**n, x) is None
    assert trigintegrate(sin(x)**n, x) is None
    assert trigintegrate(cot(x)**n, x) is None
