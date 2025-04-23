# -*- coding: utf-8 -*-
from _pytest._io.saferepr import saferepr


def test_simple_repr():
    assert saferepr(1) == "1"
    assert saferepr(None) == "None"


def test_maxsize():
    """
    Test the saferepr function with a string of maximum size.
    
    Parameters:
    maxsize (int): The maximum size of the string to be represented.
    
    Returns:
    str: A string representation of the input, truncated if necessary.
    
    This function checks the behavior of the saferepr function when applied to a long string. It ensures that the output string does not exceed the specified maximum size and includes an ellipsis ('...') if truncation occurs.
    """

    s = saferepr("x" * 50, maxsize=25)
    assert len(s) == 25
    expected = repr("x" * 10 + "..." + "x" * 10)
    assert s == expected


def test_maxsize_error_on_instance():
    class A:
        def __repr__():
            raise ValueError("...")

    s = saferepr(("*" * 50, A()), maxsize=25)
    assert len(s) == 25
    assert s[0] == "(" and s[-1] == ")"


def test_exceptions():
    class BrokenRepr:
        def __init__(self, ex):
            self.ex = ex

        def __repr__(self):
            raise self.ex

    class BrokenReprException(Exception):
        __str__ = None
        __repr__ = None

    assert "Exception" in saferepr(BrokenRepr(Exception("broken")))
    s = saferepr(BrokenReprException("really broken"))
    assert "TypeError" in s
    assert "TypeError" in saferepr(BrokenRepr("string"))

    s2 = saferepr(BrokenRepr(BrokenReprException("omg even worse")))
    assert "NameError" not in s2
    assert "unknown" in s2


def test_big_repr():
    from _pytest._io.saferepr import SafeRepr

    assert len(saferepr(range(1000))) <= len("[" + SafeRepr().maxlist * "1000" + "]")


def test_repr_on_newstyle():
    class Function(object):
        def __repr__(self):
            return "<%s>" % (self.name)

    assert saferepr(Function())


def test_unicode():
    """
    Test the safe representation of a Unicode string containing non-ASCII characters.
    
    This function checks that the safe representation of a Unicode string with special characters (GBP and Euro symbols) matches the expected string representation.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `val`: A Unicode string containing the characters '£' and '€'.
    - `reprval`: The expected string representation of `val`.
    - The function asserts that the safe representation of `val` is equal
    """

    val = u"£€"
    reprval = u"'£€'"
    assert saferepr(val) == reprval
