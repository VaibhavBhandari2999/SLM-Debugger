from sympy.matrices.densetools import trace, transpose
from sympy.matrices.densetools import eye
from sympy import ZZ

def test_trace():
    """
    Calculate the trace of a matrix.
    
    Parameters:
    a (list of lists): A square matrix represented as a list of lists of integers.
    ZZ (ring): The ring in which the trace is computed.
    
    Returns:
    ZZ: The trace of the matrix, which is the sum of the diagonal elements.
    
    Example:
    >>> test_trace()
    True
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(2, ZZ)

    assert trace(a, ZZ) == ZZ(10)
    assert trace(b, ZZ) == ZZ(2)


def test_transpose():
    """
    Transpose a matrix or the identity matrix.
    
    This function transposes a given matrix or the identity matrix if the second argument is the identity matrix.
    
    Parameters:
    a (list of lists): The matrix to be transposed. Each element is an integer.
    ZZ (object): The integer ring or the identity matrix.
    
    Returns:
    list of lists: The transposed matrix.
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
