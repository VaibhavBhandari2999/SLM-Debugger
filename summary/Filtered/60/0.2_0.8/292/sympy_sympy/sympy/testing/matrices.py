def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    Determine if two lists are element-wise close within specified tolerances.
    
    This function checks if two lists (or iterables) A and B are element-wise close to each other within the specified absolute and relative tolerances.
    
    Parameters:
    A (iterable): The first iterable to compare.
    B (iterable): The second iterable to compare.
    rtol (float, optional): The relative tolerance – it is the maximum allowed difference between A and B, relative to the larger absolute value of
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
