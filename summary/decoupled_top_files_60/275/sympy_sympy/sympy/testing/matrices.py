def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists or arrays are element-wise equal within a tolerance.
    
    This function checks whether corresponding elements of two input lists or arrays
    are equal within a given tolerance. It returns True if all elements are within
    the specified absolute and relative tolerances, and False otherwise.
    
    Parameters:
    A (list or array-like): First input list or array.
    B (list or array-like): Second input list or array.
    rtol (float, optional): The relative
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
