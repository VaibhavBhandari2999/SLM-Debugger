from sympy import Symbol, Function, exp, sqrt, Rational, I, cos, tan
from sympy.utilities.pytest import XFAIL


def test_add_eval():
    a = Symbol("a")
    b = Symbol("b")
    c = Rational(1)
    p = Rational(5)
    assert a*b + c + p == a*b + 6
    assert c + a + p == a + 6
    assert c + a - p == a + (-4)
    assert a + a == 2*a
    assert a + p + a == 2*a + 5
    assert c + p == Rational(6)
    assert b + a - b == a


def test_addmul_eval():
    """
    Evaluate and simplify symbolic expressions involving addition and multiplication.
    
    This function takes symbolic expressions and simplifies them by combining like terms and evaluating constants.
    
    Parameters:
    a (Symbol): A symbolic variable 'a'.
    b (Symbol): A symbolic variable 'b'.
    c (Rational): A rational number, default is 1.
    p (Rational): A rational number, default is 5.
    
    Returns:
    Expr: The simplified symbolic expression.
    
    Examples:
    >>> a = Symbol("a
    """

    a = Symbol("a")
    b = Symbol("b")
    c = Rational(1)
    p = Rational(5)
    assert c + a + b*c + a - p == 2*a + b + (-4)
    assert a*2 + p + a == a*2 + 5 + a
    assert a*2 + p + a == 3*a + 5
    assert a*2 + a == 3*a


def test_pow_eval():
    # XXX Pow does not fully support conversion of negative numbers
    #     to their complex equivalent

    assert sqrt(-1) == I

    assert sqrt(-4) == 2*I
    assert sqrt( 4) == 2
    assert (8)**Rational(1, 3) == 2
    assert (-8)**Rational(1, 3) == 2*((-1)**Rational(1, 3))

    assert sqrt(-2) == I*sqrt(2)
    assert (-1)**Rational(1, 3) != I
    assert (-10)**Rational(1, 3) != I*((10)**Rational(1, 3))
    assert (-2)**Rational(1, 4) != (2)**Rational(1, 4)

    assert 64**Rational(1, 3) == 4
    assert 64**Rational(2, 3) == 16
    assert 24/sqrt(64) == 3
    assert (-27)**Rational(1, 3) == 3*(-1)**Rational(1, 3)

    assert (cos(2) / tan(2))**2 == (cos(2) / tan(2))**2


@XFAIL
def test_pow_eval_X1():
    assert (-1)**Rational(1, 3) == Rational(1, 2) + Rational(1, 2)*I*sqrt(3)


def test_mulpow_eval():
    x = Symbol('x')
    assert sqrt(50)/(sqrt(2)*x) == 5/x
    assert sqrt(27)/sqrt(3) == 3


def test_evalpow_bug():
    x = Symbol("x")
    assert 1/(1/x) == x
    assert 1/(-1/x) == -x


def test_symbol_expand():
    """
    Expand a symbolic expression.
    
    This function takes two symbolic variables `x` and `y`, and a symbolic expression `f` involving these variables. It checks if `f` is equal to `x**4*y**4` and if so, returns `f` unchanged or after expanding it. Similarly, it checks if `g` is equal to `f` and if so, returns `g` unchanged or after expanding it, and ensures that multiple expansions yield the same result.
    
    Parameters:
    """

    x = Symbol('x')
    y = Symbol('y')

    f = x**4*y**4
    assert f == x**4*y**4
    assert f == f.expand()

    g = (x*y)**4
    assert g == f
    assert g.expand() == f
    assert g.expand() == g.expand().expand()


def test_function():
    """
    Test a function to verify that the product of an exponential function and its argument divided by the same exponential function simplifies to the argument itself, for both a generic function 'f' and a generic symbol 'x'.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    The function checks the simplification property for both a generic function 'f' and a generic symbol 'x'. It ensures that exp(l(x))*l(x)/exp(l(x)) simplifies to l(x) and the same for a
    """

    f = Function('f')
    l, x = map(Symbol, 'lx')
    assert exp(l(x))*l(x)/exp(l(x)) == l(x)
    assert exp(f(x))*f(x)/exp(f(x)) == f(x)
