from sympy.utilities.pytest import ignore_warnings
from sympy.utilities.exceptions import SymPyDeprecationWarning

with ignore_warnings(SymPyDeprecationWarning):
    from sympy.matrices.densetools import trace, transpose, eye

from sympy import ZZ

def test_trace():
    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(2, ZZ)

    assert trace(a, ZZ) == ZZ(10)
    assert trace(b, ZZ) == ZZ(2)


def test_transpose():
    """
    Transpose a matrix or identity matrix.
    
    This function transposes a given matrix or an identity matrix.
    
    Parameters:
    a (list of lists): A matrix represented as a list of lists, where each inner list represents a row.
    b (Matrix): An identity matrix.
    
    Keyword Arguments:
    ring (Ring): The ring in which the matrix operations are performed. Default is ZZ (integers).
    
    Returns:
    list of lists: The transposed matrix.
    Matrix: The transposed identity matrix if
    """

    a = [[ZZ(3), ZZ(7), ZZ(4)], [ZZ(2), ZZ(4), ZZ(5)], [ZZ(6), ZZ(2), ZZ(3)]]
    b = eye(4, ZZ)

    assert transpose(a, ZZ) == ([[ZZ(3), ZZ(2), ZZ(6)], [ZZ(7), ZZ(4), ZZ(2)], [ZZ(4), ZZ(5), ZZ(3)]])
    assert transpose(b, ZZ) == b
