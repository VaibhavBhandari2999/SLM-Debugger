from sympy import Symbol, Contains, S, Interval, FiniteSet, oo, Eq
from sympy.core.expr import unchanged
from sympy.utilities.pytest import raises

def test_contains_basic():
    """
    Test whether an expression is contained in a set.
    
    Parameters
    ----------
    expr : Expr
    The expression to test.
    set : FiniteSet
    The set to test against.
    
    Returns
    -------
    Boolean
    True if the expression is in the set, False otherwise.
    
    Raises
    ------
    TypeError
    If the expression is not an integer or the set is not a FiniteSet.
    """

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
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    assert Contains(x, FiniteSet(y, Eq(z, True))
        ).binary_symbols == set([y, z])


def test_as_set():
    """
    Return the set representation of the given condition.
    
    This function converts a condition involving `Contains` to its set equivalent.
    
    Parameters:
    - x (Symbol): The symbol to be checked for containment.
    - y (FiniteSet): The finite set in which the symbol is checked for membership.
    
    Returns:
    - set: The set representation of the condition.
    
    Example:
    >>> x = Symbol('x')
    >>> y = FiniteSet(Symbol('y'))
    >>> test_as_set(x, y)
    {x in {y}}
    """

    x = Symbol('x')
    y = Symbol('y')
    assert Contains(x, FiniteSet(y)
        ).as_set() == Contains(x, FiniteSet(y))
