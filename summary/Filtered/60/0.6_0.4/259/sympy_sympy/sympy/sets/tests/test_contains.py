from sympy import Symbol, Contains, S, Interval, FiniteSet, oo, Eq
from sympy.core.expr import unchanged
from sympy.utilities.pytest import raises

def test_contains_basic():
    raises(TypeError, lambda: Contains(S.Integers, 1))
    assert Contains(2, S.Integers) is S.true
    assert Contains(-2, S.Naturals) is S.false

    i = Symbol('i', integer=True)
    assert Contains(i, S.Naturals) == Contains(i, S.Naturals, evaluate=False)


def test_issue_6194():
    x = Symbol('x')
    assert unchanged(Contains, x, Interval(0, 1))
    assert Interval(0, 1).contains(x) == (S(0) <= x) & (x <= 1)
    assert Contains(x, FiniteSet(0)) != S.false
    assert Contains(x, Interval(1, 1)) != S.false
    assert Contains(x, S.Integers) != S.false


def test_issue_10326():
    assert Contains(oo, Interval(-oo, oo)) == False
    assert Contains(-oo, Interval(-oo, oo)) == False


def test_binary_symbols():
    """
    Tests if a given expression contains the specified binary symbols.
    
    This function checks if the given expression (x) contains the specified binary symbols (y and z).
    
    Parameters:
    x (Symbol): The expression to be checked.
    y (Symbol): The first binary symbol.
    z (Symbol): The second binary symbol.
    
    Returns:
    set: A set of binary symbols found in the expression.
    
    Example:
    >>> x = Symbol('x')
    >>> y = Symbol('y')
    >>> z = Symbol('z')
    >>> Contains
    """

    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    assert Contains(x, FiniteSet(y, Eq(z, True))
        ).binary_symbols == set([y, z])


def test_as_set():
    x = Symbol('x')
    y = Symbol('y')
    assert Contains(x, FiniteSet(y)
        ).as_set() == Contains(x, FiniteSet(y))
