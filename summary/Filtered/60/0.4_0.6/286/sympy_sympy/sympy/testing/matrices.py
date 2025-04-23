def allclose(A, B, rtol=1e-05, atol=1e-08):
    """
    allclose(A, B, rtol=1e-05, atol=1e-08)
    
    Compares two lists or arrays A and B to check if they are element-wise equal within a tolerance.
    
    Parameters:
    A (list or array): The first input list or array.
    B (list or array): The second input list or array.
    rtol (float, optional): The relative tolerance parameter. Default is 1e-05.
    atol (
    """

    if len(A) != len(B):
        return False

    for x, y in zip(A, B):
        if abs(x-y) > atol + rtol * max(abs(x), abs(y)):
            return False
    return True
