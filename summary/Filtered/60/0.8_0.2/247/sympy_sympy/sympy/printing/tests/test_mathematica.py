from sympy.core import (S, pi, oo, symbols, Function,
                        Rational, Integer, Tuple, Derivative)
from sympy.integrals import Integral
from sympy.concrete import Sum
from sympy.functions import exp, sin, cos, conjugate

from sympy import mathematica_code as mcode

x, y, z = symbols('x,y,z')
f = Function('f')


def test_Integer():
    assert mcode(Integer(67)) == "67"
    assert mcode(Integer(-1)) == "-1"


def test_Rational():
    """
    Test the Rational class.
    
    This function tests various operations and representations of the Rational class, including:
    - Converting a Rational number to a string using mcode.
    - Handling positive and negative Rational numbers.
    - Incorporating Rational numbers with symbolic expressions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - mcode(Rational(3, 7)) == "3/7"
    - mcode(Rational(18, 9)) == "2"
    - mcode
    """

    assert mcode(Rational(3, 7)) == "3/7"
    assert mcode(Rational(18, 9)) == "2"
    assert mcode(Rational(3, -7)) == "-3/7"
    assert mcode(Rational(-3, -7)) == "3/7"
    assert mcode(x + Rational(3, 7)) == "x + 3/7"
    assert mcode(Rational(3, 7)*x) == "(3/7)*x"


def test_Function():
    assert mcode(f(x, y, z)) == "f[x, y, z]"
    assert mcode(sin(x) ** cos(x)) == "Sin[x]^Cos[x]"
    assert mcode(conjugate(x)) == "Conjugate[x]"


def test_Pow():
    assert mcode(x**3) == "x^3"
    assert mcode(x**(y**3)) == "x^(y^3)"
    assert mcode(1/(f(x)*3.5)**(x - y**x)/(x**2 + y)) == \
        "(3.5*f[x])^(-x + y^x)/(x^2 + y)"
    assert mcode(x**-1.0) == 'x^(-1.0)'
    assert mcode(x**Rational(2, 3)) == 'x^(2/3)'


def test_Mul():
    A, B, C, D = symbols('A B C D', commutative=False)
    assert mcode(x*y*z) == "x*y*z"
    assert mcode(x*y*A) == "x*y*A"
    assert mcode(x*y*A*B) == "x*y*A**B"
    assert mcode(x*y*A*B*C) == "x*y*A**B**C"
    assert mcode(x*A*B*(C + D)*A*y) == "x*y*A**B**(C + D)**A"


def test_constants():
    assert mcode(pi) == "Pi"
    assert mcode(oo) == "Infinity"
    assert mcode(S.NegativeInfinity) == "-Infinity"
    assert mcode(S.EulerGamma) == "EulerGamma"
    assert mcode(S.Catalan) == "Catalan"
    assert mcode(S.Exp1) == "E"


def test_containers():
    """
    Test the mcode function for various container types.
    
    Args:
    containers (Union[list, tuple, Tuple]): The containers to be tested, which can be a list, tuple, or Tuple.
    
    Returns:
    str: The formatted string representation of the containers.
    
    Raises:
    None
    
    Examples:
    >>> test_containers()
    True
    """

    assert mcode([1, 2, 3, [4, 5, [6, 7]], 8, [9, 10], 11]) == \
        "{1, 2, 3, {4, 5, {6, 7}}, 8, {9, 10}, 11}"
    assert mcode((1, 2, (3, 4))) == "{1, 2, {3, 4}}"
    assert mcode([1]) == "{1}"
    assert mcode((1,)) == "{1}"
    assert mcode(Tuple(*[1, 2, 3])) == "{1, 2, 3}"


def test_Integral():
    assert mcode(Integral(sin(sin(x)), x)) == "Hold[Integrate[Sin[Sin[x]], x]]"
    assert mcode(Integral(exp(-x**2 - y**2),
                          (x, -oo, oo),
                          (y, -oo, oo))) == \
        "Hold[Integrate[Exp[-x^2 - y^2], {x, -Infinity, Infinity}, " \
        "{y, -Infinity, Infinity}]]"


def test_Derivative():
    """
    Test the Derivative function.
    
    Args:
    sin_x (str): The sine of x.
    x (str): The variable with respect to which the derivative is taken.
    y (str): The variable in the expression.
    x_order (int): The order of the derivative with respect to x.
    y_order (int): The order of the derivative with respect to y.
    
    Returns:
    str: The Mathematica code representation of the derivative.
    """

    assert mcode(Derivative(sin(x), x)) == "Hold[D[Sin[x], x]]"
    assert mcode(Derivative(x, x)) == "Hold[D[x, x]]"
    assert mcode(Derivative(sin(x)*y**4, x, 2)) == "Hold[D[y^4*Sin[x], {x, 2}]]"
    assert mcode(Derivative(sin(x)*y**4, x, y, x)) == "Hold[D[y^4*Sin[x], x, y, x]]"
    assert mcode(Derivative(sin(x)*y**4, x, y, 3, x)) == "Hold[D[y^4*Sin[x], x, {y, 3}, x]]"


def test_Sum():
    assert mcode(Sum(sin(x), (x, 0, 10))) == "Hold[Sum[Sin[x], {x, 0, 10}]]"
    assert mcode(Sum(exp(-x**2 - y**2),
                     (x, -oo, oo),
                     (y, -oo, oo))) == \
        "Hold[Sum[Exp[-x^2 - y^2], {x, -Infinity, Infinity}, " \
        "{y, -Infinity, Infinity}]]"
