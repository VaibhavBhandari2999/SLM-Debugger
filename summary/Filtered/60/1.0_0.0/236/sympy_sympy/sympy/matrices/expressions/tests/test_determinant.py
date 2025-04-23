from sympy.core import S, symbols
from sympy.matrices import eye, Matrix, ShapeError
from sympy.matrices.expressions import (
    Identity, MatrixExpr, MatrixSymbol, Determinant,
    det, ZeroMatrix, Transpose
)
from sympy.utilities.pytest import raises
from sympy import refine, Q

n = symbols('n', integer=True)
A = MatrixSymbol('A', n, n)
B = MatrixSymbol('B', n, n)
C = MatrixSymbol('C', 3, 4)


def test_det():
    """
    Calculate the determinant of a matrix.
    
    Parameters:
    A (Matrix): The matrix for which the determinant is to be calculated.
    
    Returns:
    Determinant: The determinant of the matrix A.
    
    Raises:
    ShapeError: If the input matrix A is not square.
    TypeError: If the input is not a matrix or scalar.
    
    Examples:
    >>> from sympy import Matrix, eye
    >>> A = Matrix([[1, 3, 2], [4, 1, 3], [2, 5
    """

    assert isinstance(Determinant(A), Determinant)
    assert not isinstance(Determinant(A), MatrixExpr)
    raises(ShapeError, lambda: Determinant(C))
    assert det(eye(3)) == 1
    assert det(Matrix(3, 3, [1, 3, 2, 4, 1, 3, 2, 5, 2])) == 17
    A / det(A)  # Make sure this is possible

    raises(TypeError, lambda: Determinant(S.One))

    assert Determinant(A).arg is A

def test_eval_determinant():
    """
    Test the determinant of a matrix.
    
    This function checks the determinant of different types of matrices:
    - The determinant of an identity matrix of size n should be 1.
    - The determinant of a zero matrix of size n x n should be 0.
    - The determinant of the transpose of a matrix A should be equal to the determinant of A.
    
    Parameters:
    A (Matrix): The matrix for which the determinant is calculated.
    
    Returns:
    None: This function does not return any value. It only
    """

    assert det(Identity(n)) == 1
    assert det(ZeroMatrix(n, n)) == 0
    assert det(Transpose(A)) == det(A)


def test_refine():
    assert refine(det(A), Q.orthogonal(A)) == 1
    assert refine(det(A), Q.singular(A)) == 0
