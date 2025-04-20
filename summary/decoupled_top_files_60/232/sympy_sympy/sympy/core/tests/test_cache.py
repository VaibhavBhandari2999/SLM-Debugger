from sympy.core.cache import cacheit


def test_cacheit_doc():
    """
    Cache a function's results to speed up repeated calls with the same arguments.
    
    This function decorator stores the results of function calls with specific arguments,
    reusing them if the same arguments are passed again. It helps in optimizing the performance
    of functions that are called multiple times with the same inputs.
    
    Parameters:
    None
    
    Returns:
    A wrapped function that caches its results.
    
    Example:
    >>> @cacheit
    ... def testfn():
    ...     "test docstring"
    ...
    """

    @cacheit
    def testfn():
        "test docstring"
        pass

    assert testfn.__doc__ == "test docstring"
    assert testfn.__name__ == "testfn"

def test_cacheit_unhashable():
    @cacheit
    def testit(x):
        return x

    assert testit(1) == 1
    assert testit(1) == 1
    a = {}
    assert testit(a) == {}
    a[1] = 2
    assert testit(a) == {1: 2}
