def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists are element-wise close within specified tolerances.
    
    This function checks if two lists (or iterables) A and B are element-wise close
    within the relative tolerance (rtol) and absolute tolerance (atol).
    
    Parameters:
    A (iterable): The first input iterable.
    B (iterable): The second input iterable.
    rtol (float, optional): The relative tolerance parameter (default is 1e-05).
    atol (float, optional
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
