def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists are element-wise equal within a tolerance.
    
    This function checks if two lists (or iterables) A and B are element-wise equal within a tolerance defined by rtol (relative tolerance) and atol (absolute tolerance).
    
    Parameters:
    A (iterable): The first list or iterable to compare.
    B (iterable): The second list or iterable to compare.
    rtol (float, optional): The relative tolerance parameter. Default is 1e-05.
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
