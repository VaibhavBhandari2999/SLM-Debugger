from sympy.functions import adjoint, conjugate, transpose
from sympy.matrices.expressions import MatrixSymbol, Adjoint, trace, Transpose
from sympy.matrices import eye, Matrix
from sympy import symbols, S
from sympy import refine, Q

n, m, l, k, p = symbols('n m l k p', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)


def test_transpose():
    """
    Test the transpose function for various matrix operations and properties. The function checks the transpose of a matrix, its shape, and the properties of the transpose, adjoint, and conjugate. It also tests the transpose of the identity matrix and scalar matrices. The function verifies the transpose of matrix multiplication and the invariance of the trace under transpose.
    
    Parameters:
    - A, B: MatrixSymbol instances representing matrices.
    - n, m, l: Dimensions of the matrices.
    - Sq: A square matrix
    """

    Sq = MatrixSymbol('Sq', n, n)

    assert transpose(A) == Transpose(A)
    assert Transpose(A).shape == (m, n)
    assert Transpose(A*B).shape == (l, n)
    assert transpose(Transpose(A)) == A
    assert isinstance(Transpose(Transpose(A)), Transpose)

    assert adjoint(Transpose(A)) == Adjoint(Transpose(A))
    assert conjugate(Transpose(A)) == Adjoint(A)

    assert Transpose(eye(3)).doit() == eye(3)

    assert Transpose(S(5)).doit() == S(5)

    assert Transpose(Matrix([[1, 2], [3, 4]])).doit() == Matrix([[1, 3], [2, 4]])

    assert transpose(trace(Sq)) == trace(Sq)
    assert trace(Transpose(Sq)) == trace(Sq)

    assert Transpose(Sq)[0, 1] == Sq[1, 0]

    assert Transpose(A*B).doit() == Transpose(B) * Transpose(A)


def test_transpose_MatAdd_MatMul():
    """
    Test the transpose of a matrix addition and multiplication operation.
    
    This function verifies that the transpose of the sum of a matrix N and the product of a scalar cos(x) and a matrix M is equal to the sum of the transpose of N and the product of the scalar cos(x) and the transpose of M.
    
    Parameters:
    - x (Symbol): A symbolic variable representing a scalar value.
    - M (MatrixSymbol): A symbolic matrix with 3 rows and 3 columns.
    - N (MatrixSymbol
    """

    # Issue 16807
    from sympy.functions.elementary.trigonometric import cos

    x = symbols('x')
    M = MatrixSymbol('M', 3, 3)
    N = MatrixSymbol('N', 3, 3)

    assert (N + (cos(x) * M)).T == cos(x)*M.T + N.T


def test_refine():
    assert refine(C.T, Q.symmetric(C)) == C


def test_transpose1x1():
    m = MatrixSymbol('m', 1, 1)
    assert m == refine(m.T)
    assert m == refine(m.T.T)
