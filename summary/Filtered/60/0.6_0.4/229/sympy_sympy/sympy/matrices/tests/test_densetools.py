from sympy.matrices.densetools import trace, transpose
from sympy.matrices.densetools import eye
from sympy import ZZ

def test_trace():
    """
    Calculate the trace of a matrix.
    
    Parameters:
    a (Matrix): The input matrix for which the trace is to be calculated.
    ZZ (Ring): The ring in which the trace is computed.
    
    Returns:
    Integer: The trace of the matrix as an element of the specified ring.
    
    Example:
    >>> a = [[3, 7, 4], [2, 4, 5], [6, 2, 3]]
    >>> ZZ = IntegerRing()
    >>>
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
