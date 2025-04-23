from sympy.core import S, symbols
from sympy.matrices import eye, ones, Matrix, ShapeError
from sympy.matrices.expressions import (
    Identity, MatrixExpr, MatrixSymbol, Determinant,
    det, per, ZeroMatrix, Transpose,
    Permanent
)
from sympy.matrices.expressions.special import OneMatrix
from sympy.testing.pytest import raises
from sympy.assumptions.ask import Q
from sympy.assumptions.refine import refine

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
    _ = A / det(A)  # Make sure this is possible

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
    """
    Refine the determinant of a matrix A based on its properties.
    
    This function checks the determinant of a matrix A against various properties of the matrix and returns a refined value based on those properties.
    
    Parameters:
    det (float): The determinant of the matrix A.
    Q (object): An object containing methods to test properties of the matrix A.
    
    Returns:
    float: The refined determinant value based on the matrix properties.
    
    Key Properties Tested:
    - Orthogonal matrix: The determinant should be 1.
    """

    assert refine(det(A), Q.orthogonal(A)) == 1
    assert refine(det(A), Q.singular(A)) == 0
    assert refine(det(A), Q.unit_triangular(A)) == 1
    assert refine(det(A), Q.normal(A)) == det(A)


def test_commutative():
    det_a = Determinant(A)
    det_b = Determinant(B)
    assert det_a.is_commutative
    assert det_b.is_commutative
    assert det_a * det_b == det_b * det_a

def test_permanent():
    """
    Compute the permanent of a matrix.
    
    This function calculates the permanent of a given matrix. The permanent of a matrix is similar to the determinant, but without the sign changes.
    
    Parameters:
    A (Matrix): The input matrix for which the permanent is to be calculated.
    
    Returns:
    Permanent: The permanent of the input matrix.
    
    Raises:
    TypeError: If the input is not a matrix or if the input matrix is a scalar.
    
    Examples:
    >>> from sympy import Matrix, ones
    >>>
    """

    assert isinstance(Permanent(A), Permanent)
    assert not isinstance(Permanent(A), MatrixExpr)
    assert isinstance(Permanent(C), Permanent)
    assert Permanent(ones(3, 3)).doit() == 6
    _ = C / per(C)
    assert per(Matrix(3, 3, [1, 3, 2, 4, 1, 3, 2, 5, 2])) == 103
    raises(TypeError, lambda: Permanent(S.One))
    assert Permanent(A).arg is A
