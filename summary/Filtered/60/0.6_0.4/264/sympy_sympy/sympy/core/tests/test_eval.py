from sympy import Symbol, Function, exp, sqrt, Rational, I, cos, tan, S
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
    a (Symbol): A symbolic variable.
    b (Symbol): Another symbolic variable.
    c (Rational): A rational number.
    p (Rational): Another rational number.
    
    Returns:
    Expr: The simplified symbolic expression.
    
    Examples:
    >>> a = Symbol("a")
    >>> b = Symbol("b")
    >>> c = Rational
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
    assert (-1)**Rational(1, 3) == S.Half + S.Half*I*sqrt(3)


def test_mulpow_eval():
    x = Symbol('x')
    assert sqrt(50)/(sqrt(2)*x) == 5/x
    assert sqrt(27)/sqrt(3) == 3


def test_evalpow_bug():
    """
    Tests the behavior of the SymPy function 'evalpow' which is used to simplify expressions involving division and powers.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses a Symbol 'x' to create expressions.
    - It evaluates and simplifies the expression 1/(1/x) and checks if it equals x.
    - It also evaluates and simplifies the expression 1/(-1/x) and checks if it equals -x.
    """

    x = Symbol("x")
    assert 1/(1/x) == x
    assert 1/(-1/x) == -x


def test_symbol_expand():
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
    f, l = map(Function, 'fl')
    x = Symbol('x')
    assert exp(l(x))*l(x)/exp(l(x)) == l(x)
    assert exp(f(x))*f(x)/exp(f(x)) == f(x)
