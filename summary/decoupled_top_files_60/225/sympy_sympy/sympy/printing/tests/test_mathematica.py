from sympy.core import (S, pi, oo, symbols, Function,
                        Rational, Integer, Tuple)
from sympy.integrals import Integral
from sympy.concrete import Sum
from sympy.functions import exp, sin, cos

from sympy import mathematica_code as mcode

x, y, z = symbols('x,y,z')
f = Function('f')


def test_Integer():
    assert mcode(Integer(67)) == "67"
    assert mcode(Integer(-1)) == "-1"


def test_Rational():
    assert mcode(Rational(3, 7)) == "3/7"
    assert mcode(Rational(18, 9)) == "2"
    assert mcode(Rational(3, -7)) == "-3/7"
    assert mcode(Rational(-3, -7)) == "3/7"
    assert mcode(x + Rational(3, 7)) == "x + 3/7"
    assert mcode(Rational(3, 7)*x) == "(3/7)*x"


def test_Function():
    assert mcode(f(x, y, z)) == "f[x, y, z]"
    assert mcode(sin(x) ** cos(x)) == "Sin[x]^Cos[x]"


def test_Pow():
    """
    Test the Pow function for symbolic computation.
    
    This function checks the correct formatting and conversion of various power
    expressions involving symbolic variables and mathematical operations into
    Mathematica code.
    
    Parameters:
    None
    
    Returns:
    None
    
    Examples:
    >>> test_Pow()
    # This will run the assertions and validate the Pow function's output.
    """

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
    """
    Test various mathematical constants and their representations in mcode.
    
    This function checks the correct mcode representation of several mathematical constants.
    
    Parameters:
    None
    
    Returns:
    None
    """

    assert mcode(pi) == "Pi"
    assert mcode(oo) == "Infinity"
    assert mcode(S.NegativeInfinity) == "-Infinity"
    assert mcode(S.EulerGamma) == "EulerGamma"
    assert mcode(S.Catalan) == "Catalan"
    assert mcode(S.Exp1) == "E"


def test_containers():
    """
    Test function for converting nested containers to a set-like string representation.
    
    This function takes a nested container (list or tuple) and converts it into a string representation that resembles a set, with nested structures preserved.
    
    Parameters:
    container (list or tuple): The nested container to be converted.
    
    Returns:
    str: A string representation of the container in a set-like format.
    
    Examples:
    >>> test_containers()
    "{1, 2, 3, {4, 5, {6
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


def test_Sum():
    """
    Generate a Mathematica code representation of a Sum expression.
    
    This function takes a symbolic sum expression and converts it into a string
    representing the equivalent expression in Mathematica code.
    
    Parameters:
    expr (Expression): The SymPy expression representing the sum.
    
    Returns:
    str: A string containing the Mathematica code representation of the sum.
    """

    assert mcode(Sum(sin(x), (x, 0, 10))) == "Hold[Sum[Sin[x], {x, 0, 10}]]"
    assert mcode(Sum(exp(-x**2 - y**2),
                     (x, -oo, oo),
                     (y, -oo, oo))) == \
        "Hold[Sum[Exp[-x^2 - y^2], {x, -Infinity, Infinity}, " \
        "{y, -Infinity, Infinity}]]"
