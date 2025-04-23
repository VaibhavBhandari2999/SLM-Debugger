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
    """
    Test the Trace function.
    
    This function checks the properties and operations of the Trace function for matrix expressions.
    It verifies the type of the returned object, checks for shape errors, simplifies trace expressions,
    and ensures that certain operations are possible with Trace objects.
    
    Parameters:
    A (MatrixExpr): The matrix expression for which the Trace function is tested.
    
    Returns:
    None: This function does not return any value. It prints the results of the tests.
    
    Raises:
    ShapeError: If the input matrix
    """

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
    """
    Test the trace of a mutable matrix and its addition.
    
    This function checks if the trace of a mutable matrix plus itself is equal to twice the trace of the matrix.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    X (MutableMatrix): The input mutable matrix with values [[1, 2], [3, 4]].
    
    Notes:
    - The function uses a predefined mutable matrix X with values [[1, 2], [3, 4]].
    - It
    """

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
    # Issue 9052: gave 2*Trace(MatMul(A)) instead of 2*Trace(A)
    assert trace(2*A) == 2*Trace(A)
    X = ImmutableMatrix([[1, 2], [3, 4]])
    assert trace(MatMul(2, X)) == 10


@XFAIL
def test_rewrite():
    assert isinstance(trace(A).rewrite(Sum), Sum)
instance(trace(A).rewrite(Sum), Sum)
