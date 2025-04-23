from sympy.functions import adjoint, conjugate, transpose
from sympy.matrices.expressions import MatrixSymbol, Adjoint, trace, Transpose
from sympy.matrices import eye, Matrix
from sympy.assumptions.ask import Q
from sympy.assumptions.refine import refine
from sympy.core.singleton import S
from sympy.core.symbol import symbols

n, m, l, k, p = symbols('n m l k p', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)


def test_transpose():
    """
    Test the transpose function for matrix operations.
    
    This function checks the properties and behavior of the transpose function for matrix symbols and expressions. It verifies the shape of the transposed matrix, the identity of the double transpose, and the adjoint and conjugate properties. It also tests the evaluation of the transpose and the trace of a transposed matrix.
    
    Parameters:
    - A, B: MatrixSymbol instances representing symbolic matrices.
    - n, m, l: Dimensions of the matrices (symbolic or concrete).
    -
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
    
    This function checks the transpose of the sum of a matrix N and the product of a scalar (cos(x)) and another matrix M.
    
    Parameters:
    - x (Symbol): A symbolic variable representing an angle.
    - M (MatrixSymbol): A symbolic matrix with 3 rows and 3 columns.
    - N (MatrixSymbol): A symbolic matrix with 3 rows and 3 columns.
    
    Returns:
    - Eq: The equation representing the transpose of the
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

def test_issue_9817():
    from sympy.matrices.expressions import Identity
    v = MatrixSymbol('v', 3, 1)
    A = MatrixSymbol('A', 3, 3)
    x = Matrix([i + 1 for i in range(3)])
    X = Identity(3)
    quadratic = v.T * A * v
    subbed = quadratic.xreplace({v:x, A:X})
    assert subbed.as_explicit() == Matrix([[14]])
