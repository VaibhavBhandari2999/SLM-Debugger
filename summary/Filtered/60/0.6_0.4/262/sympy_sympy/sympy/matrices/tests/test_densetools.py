from sympy.utilities.pytest import ignore_warnings
from sympy.utilities.exceptions import SymPyDeprecationWarning

with ignore_warnings(SymPyDeprecationWarning):
    from sympy.matrices.densetools import trace, transpose, eye

from sympy import ZZ

def test_trace():
    """
    Calculate the trace of a matrix.
    
    Parameters:
    a (list of lists): A square matrix represented as a list of lists.
    field (ring): The ring in which the arithmetic operations are performed.
    
    Returns:
    element: The trace of the matrix, which is the sum of the elements on the main diagonal.
    
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
    
    Args:
    a (list of lists): A matrix represented as a list of lists of integers.
    b (Matrix): The identity matrix of a specified size.
    
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
