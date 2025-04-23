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
    Test the transpose operation on matrices and matrix symbols.
    
    This function checks the properties and operations of the transpose function on matrices and matrix symbols. It verifies the shape of the transposed matrix, the identity of the transpose of a transpose, and the handling of adjoint and conjugate operations. It also tests the evaluation of the transpose of a specific matrix and the invariance of the trace under transpose.
    
    Parameters:
    - A: Matrix or MatrixSymbol representing a matrix.
    - B: Matrix or MatrixSymbol
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
    """
    Substitute matrix symbols with specific matrices and evaluate the resulting quadratic form.
    
    This function takes a quadratic form involving matrix symbols and substitutes them with specific matrices. It then evaluates the resulting expression.
    
    Parameters:
    - v (MatrixSymbol): A 3x1 matrix symbol.
    - A (MatrixSymbol): A 3x3 matrix symbol.
    - x (Matrix): A 3x1 matrix containing specific values.
    - X (Identity): A 3x3 identity matrix.
    
    Returns:
    - Matrix:
    """

    from sympy.matrices.expressions import Identity
    v = MatrixSymbol('v', 3, 1)
    A = MatrixSymbol('A', 3, 3)
    x = Matrix([i + 1 for i in range(3)])
    X = Identity(3)
    quadratic = v.T * A * v
    subbed = quadratic.xreplace({v:x, A:X})
    assert subbed.as_explicit() == Matrix([[14]])
