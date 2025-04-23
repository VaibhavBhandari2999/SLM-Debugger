# -*- coding: utf-8 -*-
from _pytest._io.saferepr import saferepr


def test_simple_repr():
    assert saferepr(1) == "1"
    assert saferepr(None) == "None"


def test_maxsize():
    """
    Test the saferepr function with a string of maximum size.
    
    This function checks the behavior of the saferepr function when applied to a string that exceeds a specified maximum size. The function truncates the string and appends an ellipsis to indicate truncation.
    
    Parameters:
    maxsize (int): The maximum size of the string before truncation.
    
    Returns:
    str: The truncated string representation with an ellipsis.
    
    Assertions:
    - The length of the returned string should be equal to the
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
    Test function for handling Unicode strings.
    
    This function checks the behavior of the `saferepr` function when applied to a Unicode string containing non-ASCII characters. The input is a Unicode string with the characters '£' and '€'. The expected output is a string representation of the input, enclosed in single quotes.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> test_unicode()
    # This should pass without any assertion error.
    """

    val = u"£€"
    reprval = u"'£€'"
    assert saferepr(val) == reprval
