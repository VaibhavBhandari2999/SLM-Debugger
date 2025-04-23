from sympy.parsing.maxima import parse_maxima
from sympy import Rational, Abs, Symbol, sin, cos, E, oo, log, factorial
from sympy.abc import x

n = Symbol('n', integer=True)


def test_parser():
    """
    Test the Maxima parser for various mathematical operations and expressions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key operations tested:
    - Parsing floating point numbers
    - Integer exponentiation
    - Trigonometric functions
    - Natural logarithm
    
    The function asserts the correctness of the parser for the given expressions.
    """

    assert Abs(parse_maxima('float(1/3)') - 0.333333333) < 10**(-5)
    assert parse_maxima('13^26') == 91733330193268616658399616009
    assert parse_maxima('sin(%pi/2) + cos(%pi/3)') == Rational(3, 2)
    assert parse_maxima('log(%e)') == 1


def test_injection():
    """
    Inject Maxima expressions into the global namespace and evaluate them.
    
    This function takes a Maxima expression and evaluates it in the current Python environment. The result of the evaluation is stored in the global variable with the same name as the expression.
    
    Parameters:
    expression (str): The Maxima expression to be evaluated.
    
    Keyword Arguments:
    globals (dict, optional): The global namespace to evaluate the expression in. Defaults to the current global namespace.
    
    Returns:
    None: The results are stored in the global
    """

    parse_maxima('c: x+1', globals=globals())
    assert c == x + 1

    parse_maxima('g: sqrt(81)', globals=globals())
    assert g == 9


def test_maxima_functions():
    assert parse_maxima('expand( (x+1)^2)') == x**2 + 2*x + 1
    assert parse_maxima('factor( x**2 + 2*x + 1)') == (x + 1)**2
    assert parse_maxima('2*cos(x)^2 + sin(x)^2') == 2*cos(x)**2 + sin(x)**2
    assert parse_maxima('trigexpand(sin(2*x)+cos(2*x))') == \
        -1 + 2*cos(x)**2 + 2*cos(x)*sin(x)
    assert parse_maxima('solve(x^2-4,x)') == [-2, 2]
    assert parse_maxima('limit((1+1/x)^x,x,inf)') == E
    assert parse_maxima('limit(sqrt(-x)/x,x,0,minus)') == -oo
    assert parse_maxima('diff(x^x, x)') == x**x*(1 + log(x))
    assert parse_maxima('sum(k, k, 1, n)', name_dict=dict(
        n=Symbol('n', integer=True),
        k=Symbol('k', integer=True)
    )) == (n**2 + n)/2
    assert parse_maxima('product(k, k, 1, n)', name_dict=dict(
        n=Symbol('n', integer=True),
        k=Symbol('k', integer=True)
    )) == factorial(n)
    assert parse_maxima('ratsimp((x^2-1)/(x+1))') == x - 1
    assert Abs( parse_maxima(
        'float(sec(%pi/3) + csc(%pi/3))') - 3.154700538379252) < 10**(-5)
