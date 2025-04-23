from sympy.concrete.products import Product
from sympy.concrete.summations import Sum
from sympy.core.function import Derivative
from sympy.core.numbers import Integer, Rational, Float, oo
from sympy.core.relational import Rel
from sympy.core.symbol import symbols
from sympy.functions import sin
from sympy.integrals.integrals import Integral
from sympy.series.order import Order

from sympy.printing.precedence import precedence, PRECEDENCE

x, y = symbols("x,y")


def test_Add():
    assert precedence(x + y) == PRECEDENCE["Add"]
    assert precedence(x*y + 1) == PRECEDENCE["Add"]


def test_Function():
    assert precedence(sin(x)) == PRECEDENCE["Func"]

def test_Derivative():
    assert precedence(Derivative(x, y)) == PRECEDENCE["Atom"]

def test_Integral():
    assert precedence(Integral(x, y)) == PRECEDENCE["Atom"]


def test_Mul():
    assert precedence(x*y) == PRECEDENCE["Mul"]
    assert precedence(-x*y) == PRECEDENCE["Add"]


def test_Number():
    """
    Test the precedence of different types of numbers in the expression tree.
    
    This function checks the precedence of various number types in the expression tree.
    It verifies that integers, rational numbers, and floating-point numbers are correctly
    assigned their respective precedence levels, as well as positive and negative infinity.
    
    Parameters:
    - Integer: An integer value.
    - Rational: A rational number represented as a fraction.
    - Float: A floating-point number.
    - oo: Positive infinity.
    - -oo: Negative infinity.
    
    Returns:
    -
    """

    assert precedence(Integer(0)) == PRECEDENCE["Atom"]
    assert precedence(Integer(1)) == PRECEDENCE["Atom"]
    assert precedence(Integer(-1)) == PRECEDENCE["Add"]
    assert precedence(Integer(10)) == PRECEDENCE["Atom"]
    assert precedence(Rational(5, 2)) == PRECEDENCE["Mul"]
    assert precedence(Rational(-5, 2)) == PRECEDENCE["Add"]
    assert precedence(Float(5)) == PRECEDENCE["Atom"]
    assert precedence(Float(-5)) == PRECEDENCE["Add"]
    assert precedence(oo) == PRECEDENCE["Atom"]
    assert precedence(-oo) == PRECEDENCE["Add"]


def test_Order():
    assert precedence(Order(x)) == PRECEDENCE["Atom"]


def test_Pow():
    assert precedence(x**y) == PRECEDENCE["Pow"]
    assert precedence(-x**y) == PRECEDENCE["Add"]
    assert precedence(x**-y) == PRECEDENCE["Pow"]


def test_Product():
    assert precedence(Product(x, (x, y, y + 1))) == PRECEDENCE["Atom"]


def test_Relational():
    assert precedence(Rel(x + y, y, "<")) == PRECEDENCE["Relational"]


def test_Sum():
    assert precedence(Sum(x, (x, y, y + 1))) == PRECEDENCE["Atom"]


def test_Symbol():
    assert precedence(x) == PRECEDENCE["Atom"]


def test_And_Or():
    # precendence relations between logical operators, ...
    assert precedence(x & y) > precedence(x | y)
    assert precedence(~y) > precedence(x & y)
    # ... and with other operators (cfr. other programming languages)
    assert precedence(x + y) > precedence(x | y)
    assert precedence(x + y) > precedence(x & y)
    assert precedence(x*y) > precedence(x | y)
    assert precedence(x*y) > precedence(x & y)
    assert precedence(~y) > precedence(x*y)
    assert precedence(~y) > precedence(x - y)
    # double checks
    assert precedence(x & y) == PRECEDENCE["And"]
    assert precedence(x | y) == PRECEDENCE["Or"]
    assert precedence(~y) == PRECEDENCE["Not"]
