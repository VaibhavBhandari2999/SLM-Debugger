import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sympy.matrices.densetools import trace, transpose
    from sympy.matrices.densetools import eye
from sympy import ZZ

def test_trace():
    """
    Compute the trace of a matrix.
    
    Parameters:
    a (list of lists): A square matrix represented as a list of lists, where each inner list represents a row.
    field (ring): The ring in which the arithmetic operations are performed.
    
    Returns:
    element: The trace of the matrix, which is the sum of the diagonal elements, as an element of the specified ring.
    
    Example:
    >>> test_trace()
    True
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(2, ZZ)

    assert trace(a, ZZ) == ZZ(10)
    assert trace(b, ZZ) == ZZ(2)


def test_transpose():
    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
