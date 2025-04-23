from sympy.assumptions import ask, Q
from sympy.assumptions.assume import assuming, global_assumptions
from sympy.abc import x, y

def test_assuming():
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
    Remove a specific assumption from the global assumptions set.
    
    This function removes the assumption that the variable `x` is an integer from the global assumptions set. It operates within a context where assumptions are temporarily applied and then removed.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Assumptions:
    - The variable `x` is initially assumed to be an integer.
    - The global assumptions set is cleared at the end of the function to ensure no residual effects on subsequent tests.
    
    Usage:
    This function
    """

    global_assumptions.add(Q.integer(x))
    with assuming():
        assert ask(Q.integer(x))
        global_assumptions.remove(Q.integer(x))
        assert not ask(Q.integer(x))
    assert ask(Q.integer(x))
    global_assumptions.clear() # for the benefit of other tests
