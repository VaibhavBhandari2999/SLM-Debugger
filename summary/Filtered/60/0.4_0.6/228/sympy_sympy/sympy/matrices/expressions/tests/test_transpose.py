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
    Test the transpose function for various matrix operations and properties.
    
    Parameters:
    A (MatrixSymbol): A symbolic matrix of shape (m, n).
    B (MatrixSymbol): Another symbolic matrix of appropriate shape for multiplication.
    n (int): Dimension for square matrix symbols.
    
    Returns:
    Various outputs including Transpose, Adjoint, and Matrix objects, and their properties.
    
    Key operations tested:
    - Transpose(A) == Transpose(A)
    - Transpose(A).shape == (m, n)
    - Transpose
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


def test_refine():
    assert refine(C.T, Q.symmetric(C)) == C


def test_transpose1x1():
    """
    Test that the transpose of a 1x1 matrix is the matrix itself.
    
    Parameters:
    m (MatrixSymbol): A symbolic matrix of dimensions 1x1.
    
    Returns:
    The original matrix, as its transpose and double-transpose are equal to itself.
    """

    m = MatrixSymbol('m', 1, 1)
    assert m == refine(m.T)
    assert m == refine(m.T.T)
