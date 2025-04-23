from sympy.core import S, symbols
from sympy.matrices import eye, Matrix, ShapeError
from sympy.matrices.expressions import (
    Identity, MatrixExpr, MatrixSymbol, Determinant,
    det, ZeroMatrix, Transpose
)
from sympy.matrices.expressions.matexpr import OneMatrix
from sympy.utilities.pytest import raises
from sympy import refine, Q

n = symbols('n', integer=True)
A = MatrixSymbol('A', n, n)
B = MatrixSymbol('B', n, n)
C = MatrixSymbol('C', 3, 4)


def test_det():
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
    Evaluate the determinant of a matrix.
    
    This function calculates the determinant of a given square matrix.
    
    Parameters:
    A (Matrix): The square matrix for which the determinant is to be calculated.
    
    Returns:
    float: The determinant of the matrix A.
    
    Key Assumptions:
    - The input matrix A is a square matrix (n x n).
    - For a 1x1 matrix, the determinant is 1.
    - For a 2x2 matrix, the determinant is 0.
    - The
    """

    assert det(Identity(n)) == 1
    assert det(ZeroMatrix(n, n)) == 0
    assert det(OneMatrix(n, n)) == Determinant(OneMatrix(n, n))
    assert det(OneMatrix(1, 1)) == 1
    assert det(OneMatrix(2, 2)) == 0
    assert det(Transpose(A)) == det(A)


def test_refine():
    assert refine(det(A), Q.orthogonal(A)) == 1
    assert refine(det(A), Q.singular(A)) == 0
