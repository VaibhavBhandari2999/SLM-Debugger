from sympy.core import Lambda, S, symbols
from sympy.concrete import Sum
from sympy.functions import adjoint, conjugate, transpose
from sympy.matrices import eye, Matrix, ShapeError, ImmutableMatrix
from sympy.matrices.expressions import (
    Adjoint, Identity, FunctionMatrix, MatrixExpr, MatrixSymbol, Trace,
    ZeroMatrix, trace, MatPow, MatAdd, MatMul
)
from sympy.utilities.pytest import raises, XFAIL

n = symbols('n', integer=True)
A = MatrixSymbol('A', n, n)
B = MatrixSymbol('B', n, n)
C = MatrixSymbol('C', 3, 4)


def test_Trace():
    assert isinstance(Trace(A), Trace)
    assert not isinstance(Trace(A), MatrixExpr)
    raises(ShapeError, lambda: Trace(C))
    assert trace(eye(3)) == 3
    assert trace(Matrix(3, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9])) == 15

    assert adjoint(Trace(A)) == trace(Adjoint(A))
    assert conjugate(Trace(A)) == trace(Adjoint(A))
    assert transpose(Trace(A)) == Trace(A)

    A / Trace(A)  # Make sure this is possible

    # Some easy simplifications
    assert trace(Identity(5)) == 5
    assert trace(ZeroMatrix(5, 5)) == 0
    assert trace(2*A*B) == 2*Trace(A*B)
    assert trace(A.T) == trace(A)

    i, j = symbols('i j')
    F = FunctionMatrix(3, 3, Lambda((i, j), i + j))
    assert trace(F) == (0 + 0) + (1 + 1) + (2 + 2)

    raises(TypeError, lambda: Trace(S.One))

    assert Trace(A).arg is A

    assert str(trace(A)) == str(Trace(A).doit())


def test_Trace_A_plus_B():
    """
    Test the trace of the sum of two matrices A and B.
    
    This function checks if the trace of the sum of two matrices A and B is equal to the sum of their individual traces. It also verifies that the argument of the resulting Trace object is the sum of the matrices A and B. Additionally, it confirms that the `doit` method returns the sum of the traces.
    
    Parameters:
    - A (Matrix): The first matrix.
    - B (Matrix): The second matrix.
    
    Returns:
    -
    """

    assert trace(A + B) == Trace(A) + Trace(B)
    assert Trace(A + B).arg == MatAdd(A, B)
    assert Trace(A + B).doit() == Trace(A) + Trace(B)


def test_Trace_MatAdd_doit():
    # See issue #9028
    X = ImmutableMatrix([[1, 2, 3]]*3)
    Y = MatrixSymbol('Y', 3, 3)
    q = MatAdd(X, 2*X, Y, -3*Y)
    assert Trace(q).arg == q
    assert Trace(q).doit() == 18 - 2*Trace(Y)


def test_Trace_MatPow_doit():
    X = Matrix([[1, 2], [3, 4]])
    assert Trace(X).doit() == 5
    q = MatPow(X, 2)
    assert Trace(q).arg == q
    assert Trace(q).doit() == 29


def test_Trace_MutableMatrix_plus():
    # See issue #9043
    X = Matrix([[1, 2], [3, 4]])
    assert Trace(X) + Trace(X) == 2*Trace(X)


def test_Trace_doit_deep_False():
    X = Matrix([[1, 2], [3, 4]])
    q = MatPow(X, 2)
    assert Trace(q).doit(deep=False).arg == q
    q = MatAdd(X, 2*X)
    assert Trace(q).doit(deep=False).arg == q
    q = MatMul(X, 2*X)
    assert Trace(q).doit(deep=False).arg == q


def test_trace_constant_factor():
    """
    Test the trace of a constant factor in matrix multiplication.
    
    This function checks if the trace of a matrix multiplied by a constant is equivalent to the constant times the trace of the matrix.
    
    Parameters:
    - A (Matrix): The matrix for which the trace is calculated.
    
    Returns:
    - bool: True if the trace of the constant times the matrix is equal to the constant times the trace of the matrix, False otherwise.
    
    Example:
    >>> from sympy import Matrix
    >>> A = Matrix([[1, 2
    """

    # Issue 9052: gave 2*Trace(MatMul(A)) instead of 2*Trace(A)
    assert trace(2*A) == 2*Trace(A)
    X = ImmutableMatrix([[1, 2], [3, 4]])
    assert trace(MatMul(2, X)) == 10


@XFAIL
def test_rewrite():
    assert isinstance(trace(A).rewrite(Sum), Sum)
