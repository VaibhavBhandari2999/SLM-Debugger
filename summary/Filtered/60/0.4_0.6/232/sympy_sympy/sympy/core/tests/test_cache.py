from sympy.core.cache import cacheit


def test_cacheit_doc():
    @cacheit
    def testfn():
        "test docstring"
        pass

    assert testfn.__doc__ == "test docstring"
    assert testfn.__name__ == "testfn"

def test_cacheit_unhashable():
    """
    Test the caching functionality with unhashable arguments.
    
    This function tests the `cacheit` decorator to ensure it correctly handles
    unhashable arguments. The `testit` function is decorated with `cacheit` to
    cache its results. The function is called twice with the same integer argument
    and once with a dictionary argument. The dictionary is modified between calls
    to ensure the cache is not affected by changes to mutable arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
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
