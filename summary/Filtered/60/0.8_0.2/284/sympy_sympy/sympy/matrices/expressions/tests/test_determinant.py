from sympy.core import S, symbols
from sympy.matrices import eye, Matrix, ShapeError
from sympy.matrices.expressions import (
    Identity, MatrixExpr, MatrixSymbol, Determinant,
    det, ZeroMatrix, Transpose
)
from sympy.matrices.expressions.special import OneMatrix
from sympy.testing.pytest import raises
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
    assert det(Identity(n)) == 1
    assert det(ZeroMatrix(n, n)) == 0
    assert det(OneMatrix(n, n)) == Determinant(OneMatrix(n, n))
    assert det(OneMatrix(1, 1)) == 1
    assert det(OneMatrix(2, 2)) == 0
    assert det(Transpose(A)) == det(A)


def test_refine():
    assert refine(det(A), Q.orthogonal(A)) == 1
    assert refine(det(A), Q.singular(A)) == 0


def test_commutative():
    """
    Test the commutative property of determinants.
    
    This function checks if the determinants of two matrices, A and B, are commutative under multiplication.
    
    Parameters:
    A (Matrix): The first matrix to compute the determinant for.
    B (Matrix): The second matrix to compute the determinant for.
    
    Returns:
    None: This function does not return any value. It asserts that the determinants are commutative.
    
    Notes:
    - The function asserts that the determinants of A and
    """

    det_a = Determinant(A)
    det_b = Determinant(B)
    assert det_a.is_commutative
    assert det_b.is_commutative
    assert det_a * det_b == det_b * det_a
 det_a * det_b == det_b * det_a
