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
    
    This function computes the determinant of a given matrix A. It returns a Determinant object, which is not a MatrixExpr. If the input is not a 3x3 matrix, a ShapeError is raised. The function also ensures that the division of the matrix by its determinant is possible.
    
    Parameters:
    A (Matrix): The input matrix for which the determinant is to be calculated.
    
    Returns:
    Determinant: The determinant of the input matrix as a Determinant object
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
    
    This function evaluates the determinant of various matrices to ensure correctness.
    
    Parameters:
    A (Matrix): The matrix for which the determinant is to be calculated.
    
    Returns:
    float: The determinant of the input matrix.
    
    Raises:
    ValueError: If the input matrix is not square.
    
    Key Notes:
    - The determinant of an identity matrix of size n is 1.
    - The determinant of a zero matrix of size n x n is 0.
    - The
    """

    assert det(Identity(n)) == 1
    assert det(ZeroMatrix(n, n)) == 0
    assert det(Transpose(A)) == det(A)


def test_refine():
    assert refine(det(A), Q.orthogonal(A)) == 1
    assert refine(det(A), Q.singular(A)) == 0
