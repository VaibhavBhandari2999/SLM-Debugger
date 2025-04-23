# -*- coding: utf-8 -*-
from _pytest._io.saferepr import saferepr


def test_simple_repr():
    assert saferepr(1) == "1"
    assert saferepr(None) == "None"


def test_maxsize():
    """
    Test the saferepr function with a string of maximum size.
    
    This function checks the behavior of the saferepr function when applied to a string that exceeds a specified maximum size. The string is truncated to the maximum size, and an ellipsis is inserted to indicate the truncation.
    
    Parameters:
    maxsize (int): The maximum size allowed for the string representation.
    
    Returns:
    str: The string representation of the input string, truncated and with an ellipsis if necessary.
    
    Example:
    >>>
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
    """
    Test the representation of a large list to ensure it does not exceed a certain length.
    
    This function checks if the representation of a large list (1000 elements) does not exceed a predefined maximum length. It uses the `saferepr` function from `_pytest._io.saferepr` to safely represent the list and compares the length of the resulting string with the maximum allowed length.
    
    Parameters:
    None
    
    Returns:
    bool: True if the representation length is within the allowed
    """

    from _pytest._io.saferepr import SafeRepr

    assert len(saferepr(range(1000))) <= len("[" + SafeRepr().maxlist * "1000" + "]")


def test_repr_on_newstyle():
    class Function(object):
        def __repr__(self):
            return "<%s>" % (self.name)

    assert saferepr(Function())


def test_unicode():
    val = u"£€"
    reprval = u"'£€'"
    assert saferepr(val) == reprval
