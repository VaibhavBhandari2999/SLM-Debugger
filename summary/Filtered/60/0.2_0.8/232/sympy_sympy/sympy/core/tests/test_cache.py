from sympy.core.cache import cacheit


def test_cacheit_doc():
    """
    Cache a function's results to speed up repeated calls with the same arguments.
    
    This function decorator stores the results of function calls based on their arguments,
    reducing the need to recompute results for the same inputs. It is particularly useful
    for functions that are computationally expensive or involve I/O operations.
    
    Parameters:
    None
    
    Returns:
    A wrapped function that caches its results.
    
    Example:
    >>> @cacheit
    ... def testfn():
    ...     "test docstring"
    """

    @cacheit
    def testfn():
        "test docstring"
        pass

    assert testfn.__doc__ == "test docstring"
    assert testfn.__name__ == "testfn"

def test_cacheit_unhashable():
    """
    Test the cacheit decorator with unhashable arguments.
    
    This function tests the behavior of the `cacheit` decorator when used with unhashable arguments. It checks if the decorator correctly handles mutable objects like dictionaries.
    
    Parameters:
    x: The input argument, which can be any type, including unhashable types like dictionaries.
    
    Returns:
    The input argument `x` is returned unchanged.
    
    Example usage:
    >>> test_cacheit_unhashable()
    None
    """

    @cacheit
    def testit(x):
        return x

    assert testit(1) == 1
    assert testit(1) == 1
    a = {}
    assert testit(a) == {}
    a[1] = 2
    assert testit(a) == {1: 2}
