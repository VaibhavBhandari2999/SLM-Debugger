import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
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
    Transpose a matrix or the identity matrix.
    
    Args:
    a (list of lists): A matrix represented as a list of lists of integers.
    field (ring): The ring in which the matrix elements are defined.
    
    Returns:
    list of lists: The transposed matrix.
    
    Examples:
    >>> test_transpose()
    True
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
