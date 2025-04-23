def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists are element-wise equal within a tolerance.
    
    This function checks if two lists (or iterables) A and B are element-wise equal within a tolerance defined by rtol (relative tolerance) and atol (absolute tolerance).
    
    Parameters:
    A (iterable): First input iterable.
    B (iterable): Second input iterable.
    rtol (float, optional): The relative tolerance parameter (default is 1e-05).
    atol (float, optional): The
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
