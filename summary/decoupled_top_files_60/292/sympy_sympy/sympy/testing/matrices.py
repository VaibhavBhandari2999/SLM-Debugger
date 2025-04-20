def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists are element-wise close within specified tolerances.
    
    Parameters:
    A (list): First list of numbers to compare.
    B (list): Second list of numbers to compare.
    rtol (float, optional): The relative tolerance parameter (default is 1e-05).
    atol (float, optional): The absolute tolerance parameter (default is 1e-08).
    
    Returns:
    bool: True if all elements of the two lists are within the given
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
