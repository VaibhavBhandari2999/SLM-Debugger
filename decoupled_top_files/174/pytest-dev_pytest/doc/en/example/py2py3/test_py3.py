def test_exception_syntax():
    """
    Test exception handling with ZeroDivisionError.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    ZeroDivisionError: When attempting to divide by zero.
    
    Example:
    >>> test_exception_syntax()
    AssertionError: The division by zero was handled correctly.
    """

    try:
        0 / 0
    except ZeroDivisionError as e:
        assert e
