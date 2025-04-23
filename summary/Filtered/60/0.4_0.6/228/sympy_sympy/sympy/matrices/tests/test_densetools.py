from sympy.matrices.densetools import trace, transpose
from sympy.matrices.densetools import eye
from sympy import ZZ

def test_trace():
    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(2, ZZ)

    assert trace(a, ZZ) == ZZ(10)
    assert trace(b, ZZ) == ZZ(2)


def test_transpose():
    """
    Transpose a matrix or identity matrix.
    
    This function takes a matrix `a` or an identity matrix `b` and returns its transpose. The matrix elements are assumed to be of type `ZZ` (integers).
    
    Parameters:
    a (list of list of ZZ): A 2D list representing a matrix with integer entries.
    b (Matrix): An identity matrix of type Matrix with integer entries.
    
    Returns:
    list of list of ZZ: The transposed matrix.
    
    Examples:
    >>> test
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
