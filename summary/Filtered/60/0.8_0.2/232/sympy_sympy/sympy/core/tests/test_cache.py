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
    Tests the behavior of the `cacheit` decorator with unhashable types.
    
    This function checks how the `cacheit` decorator handles unhashable objects, such as dictionaries, by caching the results of the `testit` function. The `testit` function simply returns its input. The function creates a dictionary `a` and passes it to `testit`. After modifying the dictionary, it calls `testit` again to verify that the cached result is returned for the unmodified dictionary
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
