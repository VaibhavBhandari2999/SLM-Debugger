from sympy.assumptions import ask, Q
from sympy.assumptions.assume import assuming, global_assumptions
from sympy.abc import x, y

def test_assuming():
    """
    Test the 'assuming' context manager for integer constraints.
    
    This function demonstrates the usage of the 'assuming' context manager to check if a symbolic variable 'x' is assumed to be an integer within the context. It asserts that 'x' is integer within the context, but not outside of it.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    - x: A symbolic variable.
    
    Example:
    >>> test_assuming()
    """

    with assuming(Q.integer(x)):
        assert ask(Q.integer(x))
    assert not ask(Q.integer(x))

def test_assuming_nested():
    assert not ask(Q.integer(x))
    assert not ask(Q.integer(y))
    with assuming(Q.integer(x)):
        assert ask(Q.integer(x))
        assert not ask(Q.integer(y))
        with assuming(Q.integer(y)):
            assert ask(Q.integer(x))
            assert ask(Q.integer(y))
        assert ask(Q.integer(x))
        assert not ask(Q.integer(y))
    assert not ask(Q.integer(x))
    assert not ask(Q.integer(y))

def test_finally():
    try:
        with assuming(Q.integer(x)):
            1/0
    except ZeroDivisionError:
        pass
    assert not ask(Q.integer(x))

def test_remove_safe():
    """
    Remove a specific assumption from the global assumptions set and verify the state of the assumptions.
    
    This function operates within the context of symbolic computation and logical reasoning, where assumptions about variables are maintained and can be cleared.
    
    Key Parameters:
    - None
    
    Keywords:
    - None
    
    Returns:
    - None
    
    Description:
    1. Adds an assumption that `x` is an integer to the global assumptions set.
    2. Enters a context where the assumption is considered true.
    3. Verifies that the assumption is true.
    """

    global_assumptions.add(Q.integer(x))
    with assuming():
        assert ask(Q.integer(x))
        global_assumptions.remove(Q.integer(x))
        assert not ask(Q.integer(x))
    assert ask(Q.integer(x))
    global_assumptions.clear() # for the benefit of other tests
