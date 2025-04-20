# -*- coding: utf-8 -*-
from _pytest._io.saferepr import saferepr


def test_simple_repr():
    assert saferepr(1) == "1"
    assert saferepr(None) == "None"


def test_maxsize():
    s = saferepr("x" * 50, maxsize=25)
    assert len(s) == 25
    expected = repr("x" * 10 + "..." + "x" * 10)
    assert s == expected


def test_maxsize_error_on_instance():
    """
    Generate a safe representation of a tuple containing a string and an instance of a custom class A. The function limits the length of the representation to 25 characters by truncating it if necessary. The custom class A raises a ValueError in its __repr__ method. The function returns a string representation of the tuple, ensuring that the representation does not exceed the specified maximum size.
    
    Parameters:
    - maxsize (int): The maximum allowed size of the returned string representation.
    
    Returns:
    - str: A truncated
    """

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
    Test the representation of a large list using the SafeRepr class.
    
    This function checks that the string representation of a large list (1000 elements) does not exceed a certain length limit.
    
    Parameters:
    None
    
    Returns:
    bool: True if the representation length is within the expected limit, False otherwise.
    """

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
    
    This function checks the safe representation of a Unicode string containing special characters.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses the `saferepr` function to safely represent the Unicode string.
    - The input string `val` contains the characters '£' and '€'.
    - The expected output is a string representation of the input, enclosed in single quotes.
    
    Example:
    >>> test_unicode()
    None
    """

    val = u"£€"
    reprval = u"'£€'"
    assert saferepr(val) == reprval
