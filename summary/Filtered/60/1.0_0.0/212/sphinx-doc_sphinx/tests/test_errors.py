import sys

from sphinx.errors import ExtensionError


def test_extension_error_repr():
    exc = ExtensionError("foo")
    assert repr(exc) == "ExtensionError('foo')"


def test_extension_error_with_orig_exc_repr():
    """
    Generate a Python docstring for the provided function.
    
    This function tests the representation of an `ExtensionError` with an original exception. It checks if the representation matches the expected output based on the Python version.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    None
    
    Example:
    >>> test_extension_error_with_orig_exc_repr()
    # The function will assert that the representation of the `ExtensionError` matches the expected string.
    """

    exc = ExtensionError("foo", Exception("bar"))
    if sys.version_info < (3, 7):
        expected = "ExtensionError('foo', Exception('bar',))"
    else:
        expected = "ExtensionError('foo', Exception('bar'))"
    assert repr(exc) == expected
