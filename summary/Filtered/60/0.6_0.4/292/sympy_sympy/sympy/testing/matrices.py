def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Compare two sequences (A and B) for approximate equality within a tolerance.
    
    Parameters:
    A (iterable): The first sequence to compare.
    B (iterable): The second sequence to compare.
    rtol (float, optional): The relative tolerance parameter (default is 1e-05).
    atol (float, optional): The absolute tolerance parameter (default is 1e-08).
    
    Returns:
    bool: True if the sequences are approximately equal within the given toler
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
