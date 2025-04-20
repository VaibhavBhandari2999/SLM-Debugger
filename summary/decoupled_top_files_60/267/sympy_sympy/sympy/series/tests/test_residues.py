from sympy import (residue, Symbol, Function, sin, I, exp, log, pi,
                   factorial, sqrt, Rational)
from sympy.utilities.pytest import XFAIL, raises
from sympy.abc import x, z, a, s


def test_basic1():
    assert residue(1/x, x, 0) == 1
    assert residue(-2/x, x, 0) == -2
    assert residue(81/x, x, 0) == 81
    assert residue(1/x**2, x, 0) == 0
    assert residue(0, x, 0) == 0
    assert residue(5, x, 0) == 0
    assert residue(x, x, 0) == 0
    assert residue(x**2, x, 0) == 0


def test_basic2():
    """
    Test the residue function with various inputs.
    
    Parameters:
    - expression (sympy expression): The mathematical expression for which the residue needs to be calculated.
    - variable (sympy symbol): The variable with respect to which the residue is to be found.
    - point (float or sympy symbol): The point at which the residue is to be evaluated.
    
    Returns:
    - int or float: The residue of the given expression at the specified point.
    
    Key Points:
    - The function
    """

    assert residue(1/x, x, 1) == 0
    assert residue(-2/x, x, 1) == 0
    assert residue(81/x, x, -1) == 0
    assert residue(1/x**2, x, 1) == 0
    assert residue(0, x, 1) == 0
    assert residue(5, x, 1) == 0
    assert residue(x, x, 1) == 0
    assert residue(x**2, x, 5) == 0


def test_f():
    f = Function("f")
    assert residue(f(x)/x**5, x, 0) == f(x).diff(x, 4).subs(x, 0)/24


def test_functions():
    """
    Test the residue function with various inputs.
    
    Parameters:
    x (Symbol): The variable in the expression.
    expr (Expression): The mathematical expression for which the residue needs to be calculated.
    
    This function tests the residue function with different expressions and their respective variables. It checks the residue at the specified point and returns the result.
    
    Key Parameters:
    x (Symbol): The variable in the expression.
    expr (Expression): The mathematical expression for which the residue needs to be calculated.
    
    Returns:
    int
    """

    assert residue(1/sin(x), x, 0) == 1
    assert residue(2/sin(x), x, 0) == 2
    assert residue(1/sin(x)**2, x, 0) == 0
    assert residue(1/sin(x)**5, x, 0) == Rational(3, 8)


def test_expressions():
    """
    Test various residue calculations.
    
    This function checks the correctness of the residue calculation for different
    expressions and poles. It verifies the residue at 0, -1, and complex points
    for various rational functions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The residue of 1/(x + 1) at x = 0 is 0.
    - The residue of 1/(x + 1) at x = -1 is 1.
    -
    """

    assert residue(1/(x + 1), x, 0) == 0
    assert residue(1/(x + 1), x, -1) == 1
    assert residue(1/(x**2 + 1), x, -1) == 0
    assert residue(1/(x**2 + 1), x, I) == -I/2
    assert residue(1/(x**2 + 1), x, -I) == I/2
    assert residue(1/(x**4 + 1), x, 0) == 0
    assert residue(1/(x**4 + 1), x, exp(I*pi/4)).equals(-(Rational(1, 4) + I/4)/sqrt(2))
    assert residue(1/(x**2 + a**2)**2, x, a*I) == -I/4/a**3


@XFAIL
def test_expressions_failing():
    n = Symbol('n', integer=True, positive=True)
    assert residue(exp(z)/(z - pi*I/4*a)**n, z, I*pi*a) == \
        exp(I*pi*a/4)/factorial(n - 1)


def test_NotImplemented():
    raises(NotImplementedError, lambda: residue(exp(1/z), z, 0))


def test_bug():
    assert residue(2**(z)*(s + z)*(1 - s - z)/z**2, z, 0) == \
        1 + s*log(2) - s**2*log(2) - 2*s


def test_issue_5654():
    assert residue(1/(x**2 + a**2)**2, x, a*I) == -I/(4*a**3)


def test_issue_6499():
    assert residue(1/(exp(z) - 1), z, 0) == 1
a**3)


def test_issue_6499():
    assert residue(1/(exp(z) - 1), z, 0) == 1
