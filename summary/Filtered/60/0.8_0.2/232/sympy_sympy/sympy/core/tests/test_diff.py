from sympy import Symbol, Rational, cos, sin, tan, cot, exp, log, Function, \
    Derivative, Expr, symbols, pi, I, S
from sympy.utilities.pytest import raises


def test_diff():
    """
    Test the differentiation of symbolic expressions and constants.
    
    This function checks the differentiation of various symbolic expressions and constants with respect to a given variable. It also tests the differentiation with respect to multiple variables and the handling of invalid inputs.
    
    Parameters:
    - x, y: Symbols representing variables in the expressions.
    
    Returns:
    - None: The function asserts the correctness of the differentiation results.
    
    Key Assertions:
    - The derivative of a rational number with respect to any variable is zero.
    - The derivative of the imaginary unit (I
    """

    x, y = symbols('x, y')
    assert Rational(1, 3).diff(x) is S.Zero
    assert I.diff(x) is S.Zero
    assert pi.diff(x) is S.Zero
    assert x.diff(x, 0) == x
    assert (x**2).diff(x, 2, x) == 0
    assert (x**2).diff(x, y, 0) == 2*x
    assert (x**2).diff(x, y) == 0
    raises(ValueError, lambda: x.diff(1, x))

    a = Symbol("a")
    b = Symbol("b")
    c = Symbol("c")
    p = Rational(5)
    e = a*b + b**p
    assert e.diff(a) == b
    assert e.diff(b) == a + 5*b**4
    assert e.diff(b).diff(a) == Rational(1)
    e = a*(b + c)
    assert e.diff(a) == b + c
    assert e.diff(b) == a
    assert e.diff(b).diff(a) == Rational(1)
    e = c**p
    assert e.diff(c, 6) == Rational(0)
    assert e.diff(c, 5) == Rational(120)
    e = c**Rational(2)
    assert e.diff(c) == 2*c
    e = a*b*c
    assert e.diff(c) == a*b


def test_diff2():
    n3 = Rational(3)
    n2 = Rational(2)
    n6 = Rational(6)
    x, c = map(Symbol, 'xc')

    e = n3*(-n2 + x**n2)*cos(x) + x*(-n6 + x**n2)*sin(x)
    assert e == 3*(-2 + x**2)*cos(x) + x*(-6 + x**2)*sin(x)
    assert e.diff(x).expand() == x**3*cos(x)

    e = (x + 1)**3
    assert e.diff(x) == 3*(x + 1)**2
    e = x*(x + 1)**3
    assert e.diff(x) == (x + 1)**3 + 3*x*(x + 1)**2
    e = 2*exp(x*x)*x
    assert e.diff(x) == 2*exp(x**2) + 4*x**2*exp(x**2)


def test_diff3():
    a, b, c = map(Symbol, 'abc')
    p = Rational(5)
    e = a*b + sin(b**p)
    assert e == a*b + sin(b**5)
    assert e.diff(a) == b
    assert e.diff(b) == a + 5*b**4*cos(b**5)
    e = tan(c)
    assert e == tan(c)
    assert e.diff(c) in [cos(c)**(-2), 1 + sin(c)**2/cos(c)**2, 1 + tan(c)**2]
    e = c*log(c) - c
    assert e == -c + c*log(c)
    assert e.diff(c) == log(c)
    e = log(sin(c))
    assert e == log(sin(c))
    assert e.diff(c) in [sin(c)**(-1)*cos(c), cot(c)]
    e = (Rational(2)**a/log(Rational(2)))
    assert e == 2**a*log(Rational(2))**(-1)
    assert e.diff(a) == 2**a


def test_diff_no_eval_derivative():
    class My(Expr):
        def __new__(cls, x):
            return Expr.__new__(cls, x)

    x, y = symbols('x y')
    # My doesn't have its own _eval_derivative method
    assert My(x).diff(x).func is Derivative
    # it doesn't have y so it shouldn't need a method for this case
    assert My(x).diff(y) == 0


def test_speed():
    """
    Test the differentiation of a symbolic variable with respect to itself for a large number of times.
    
    This function checks the correctness of the differentiation operation in the symbolic math library. It differentiates the symbol 'x' with respect to itself 10^8 times and asserts that the result is zero, as the derivative of any variable with respect to itself is always 1, and the 10^8th derivative would be zero.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError:
    """

    # this should return in 0.0s. If it takes forever, it's wrong.
    x = Symbol("x")
    assert x.diff(x, 10**8) == 0


def test_deriv_noncommutative():
    A = Symbol("A", commutative=False)
    f = Function("f")
    x = Symbol("x")
    assert A*f(x)*A == f(x)*A**2
    assert A*f(x).diff(x)*A == f(x).diff(x) * A**2
