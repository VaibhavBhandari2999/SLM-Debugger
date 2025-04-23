from sympy.core.cache import cacheit


def test_cacheit_doc():
    """
    Cache a function's results to speed up repeated calls with the same arguments.
    
    This function takes a function as input and returns a new function that caches the results of the original function. The cached results are stored in a dictionary, and the new function checks if the result for a given set of arguments is already in the cache before computing it. If the result is found in the cache, it is returned immediately, otherwise, the original function is called and the result is stored in the cache for future calls
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
}
