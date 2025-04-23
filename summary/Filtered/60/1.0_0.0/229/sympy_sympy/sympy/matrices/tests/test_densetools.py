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
    Transpose a matrix.
    
    This function takes a matrix `a` and transposes it, swapping its rows and columns. The function also accepts a `ring` parameter which specifies the type of elements in the resulting matrix.
    
    Parameters:
    a (list of lists): The input matrix to be transposed.
    ring (Ring): The ring type for the elements of the resulting matrix.
    
    Returns:
    list of lists: The transposed matrix with elements of the specified ring type.
    
    Example:
    >>> test
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
