from sympy.core.logic import (fuzzy_not, Logic, And, Or, Not, fuzzy_and,
    fuzzy_or, _fuzzy_group, _torf)
from sympy.utilities.pytest import raises

T = True
F = False
U = None


def test_torf():
    """
    Test the truth value of a 3-tuple of logical values.
    
    This function evaluates the truth value of all possible combinations of a 3-tuple
    containing the logical values True (T), False (F), and Undefined (U). It checks if
    all elements in the tuple are True, all elements are False, or if the tuple contains
    both True and False values, in which case it returns None.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> test
    """

    from sympy.utilities.iterables import cartes
    v = [T, F, U]
    for i in cartes(*[v]*3):
        assert _torf(i) is (
            True if all(j for j in i) else (False if all(j is False for j in i) else None))


def test_fuzzy_group():
    """
    Test fuzzy group functionality.
    
    This function tests the `_fuzzy_group` function, which evaluates the logical
    grouping of fuzzy values. The function takes a tuple of values from the set
    {True, False, None} and returns the logical group based on the following rules:
    - If any value is None, the result is None.
    - If all values are True, the result is True.
    - If there is more than one False value, the result is None.
    - Otherwise, the result
    """

    from sympy.utilities.iterables import cartes
    v = [T, F, U]
    for i in cartes(*[v]*3):
        assert _fuzzy_group(i) is (
            None if None in i else (
            True if all(j for j in i) else False))
        assert _fuzzy_group(i, quick_exit=True) is (
            None if (i.count(False) > 1) else (None if None in i else (
            True if all(j for j in i) else False)))
    it = (True if (i == 0) else None for i in range(2))
    assert _torf(it) is None
    it = (True if (i == 1) else None for i in range(2))
    assert _torf(it) is None


def test_fuzzy_not():
    assert fuzzy_not(T) == F
    assert fuzzy_not(F) == T
    assert fuzzy_not(U) == U


def test_fuzzy_and():
    assert fuzzy_and([T, T]) == T
    assert fuzzy_and([T, F]) == F
    assert fuzzy_and([T, U]) == U
    assert fuzzy_and([F, F]) == F
    assert fuzzy_and([F, U]) == F
    assert fuzzy_and([U, U]) == U
    assert [fuzzy_and([w]) for w in [U, T, F]] == [U, T, F]
    assert fuzzy_and([T, F, U]) == F
    assert fuzzy_and([]) == T
    raises(TypeError, lambda: fuzzy_and())


def test_fuzzy_or():
    assert fuzzy_or([T, T]) == T
    assert fuzzy_or([T, F]) == T
    assert fuzzy_or([T, U]) == T
    assert fuzzy_or([F, F]) == F
    assert fuzzy_or([F, U]) == U
    assert fuzzy_or([U, U]) == U
    assert [fuzzy_or([w]) for w in [U, T, F]] == [U, T, F]
    assert fuzzy_or([T, F, U]) == T
    assert fuzzy_or([]) == F
    raises(TypeError, lambda: fuzzy_or())


def test_logic_cmp():
    l1 = And('a', Not('b'))
    l2 = And('a', Not('b'))

    assert hash(l1) == hash(l2)
    assert (l1 == l2) == T
    assert (l1 != l2) == F

    assert And('a', 'b', 'c') == And('b', 'a', 'c')
    assert And('a', 'b', 'c') == And('c', 'b', 'a')
    assert And('a', 'b', 'c') == And('c', 'a', 'b')


def test_logic_onearg():
    assert And() is True
    assert Or() is False

    assert And(T) == T
    assert And(F) == F
    assert Or(T) == T
    assert Or(F) == F

    assert And('a') == 'a'
    assert Or('a') == 'a'


def test_logic_xnotx():
    assert And('a', Not('a')) == F
    assert Or('a', Not('a')) == T


def test_logic_eval_TF():
    """
    Test logical operations.
    
    This function evaluates logical operations (AND and OR) on boolean values and
    strings. It checks the behavior of these operations with different inputs and
    returns the expected results.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key operations:
    - AND operation:
    - And(F, F) -> F
    - And(F, T) -> F
    - And(T, F) -> F
    - And(T, T) -> T
    - OR operation
    """

    assert And(F, F) == F
    assert And(F, T) == F
    assert And(T, F) == F
    assert And(T, T) == T

    assert Or(F, F) == F
    assert Or(F, T) == T
    assert Or(T, F) == T
    assert Or(T, T) == T

    assert And('a', T) == 'a'
    assert And('a', F) == F
    assert Or('a', T) == T
    assert Or('a', F) == 'a'


def test_logic_combine_args():
    assert And('a', 'b', 'a') == And('a', 'b')
    assert Or('a', 'b', 'a') == Or('a', 'b')

    assert And( And('a', 'b'), And('c', 'd') ) == And('a', 'b', 'c', 'd')
    assert Or( Or('a', 'b'), Or('c', 'd') ) == Or('a', 'b', 'c', 'd')

    assert Or( 't', And('n', 'p', 'r'), And('n', 'r'), And('n', 'p', 'r'), 't', And('n', 'r') ) == \
        Or('t', And('n', 'p', 'r'), And('n', 'r'))


def test_logic_expand():
    t = And(Or('a', 'b'), 'c')
    assert t.expand() == Or(And('a', 'c'), And('b', 'c'))

    t = And(Or('a', Not('b')), 'b')
    assert t.expand() == And('a', 'b')

    t = And(Or('a', 'b'), Or('c', 'd'))
    assert t.expand() == \
        Or(And('a', 'c'), And('a', 'd'), And('b', 'c'), And('b', 'd'))


def test_logic_fromstring():
    S = Logic.fromstring

    assert S('a') == 'a'
    assert S('!a') == Not('a')
    assert S('a & b') == And('a', 'b')
    assert S('a | b') == Or('a', 'b')
    assert S('a | b & c') == And(Or('a', 'b'), 'c')
    assert S('a & b | c') == Or(And('a', 'b'), 'c')
    assert S('a & b & c') == And('a', 'b', 'c')
    assert S('a | b | c') == Or('a', 'b', 'c')

    raises(ValueError, lambda: S('| a'))
    raises(ValueError, lambda: S('& a'))
    raises(ValueError, lambda: S('a | | b'))
    raises(ValueError, lambda: S('a | & b'))
    raises(ValueError, lambda: S('a & & b'))
    raises(ValueError, lambda: S('a |'))
    raises(ValueError, lambda: S('a|b'))
    raises(ValueError, lambda: S('!'))
    raises(ValueError, lambda: S('! a'))


def test_logic_not():
    assert Not('a') != '!a'
    assert Not('!a') != 'a'

    # NOTE: we may want to change default Not behaviour and put this
    # functionality into some method.
    assert Not(And('a', 'b')) == Or(Not('a'), Not('b'))
    assert Not(Or('a', 'b')) == And(Not('a'), Not('b'))


def test_formatting():
    S = Logic.fromstring
    raises(ValueError, lambda: S('a&b'))
    raises(ValueError, lambda: S('a|b'))
    raises(ValueError, lambda: S('! a'))
rror, lambda: S('! a'))
