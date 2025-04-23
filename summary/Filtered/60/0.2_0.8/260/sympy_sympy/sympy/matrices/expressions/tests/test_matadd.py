from sympy.matrices.expressions import MatrixSymbol, MatAdd, MatPow, MatMul
from sympy.matrices.expressions.matexpr import GenericZeroMatrix
from sympy.matrices import eye, ImmutableMatrix
from sympy.core import Basic, S

X = MatrixSymbol('X', 2, 2)
Y = MatrixSymbol('Y', 2, 2)

def test_sort_key():
    assert MatAdd(Y, X).doit().args == (X, Y)


def test_matadd_sympify():
    assert isinstance(MatAdd(eye(1), eye(1)).args[0], Basic)


def test_matadd_of_matrices():
    assert MatAdd(eye(2), 4*eye(2), eye(2)).doit() == ImmutableMatrix(6*eye(2))


def test_doit_args():
    """
    Perform matrix operations and simplify expressions.
    
    This function evaluates matrix addition, exponentiation, and multiplication
    using the `doit` method. It supports multiple operations and simplifies the
    resulting expression.
    
    Parameters:
    A (ImmutableMatrix): The first matrix.
    B (ImmutableMatrix): The second matrix.
    X (ImmutableMatrix, optional): An additional matrix for addition.
    Y (ImmutableMatrix, optional): Another additional matrix for addition.
    MatAdd (class): The matrix addition class
    """

    A = ImmutableMatrix([[1, 2], [3, 4]])
    B = ImmutableMatrix([[2, 3], [4, 5]])
    assert MatAdd(A, MatPow(B, 2)).doit() == A + B**2
    assert MatAdd(A, MatMul(A, B)).doit() == A + A*B
    assert (MatAdd(A, X, MatMul(A, B), Y, MatAdd(2*A, B)).doit() ==
            MatAdd(3*A + A*B + B, X, Y))


def test_generic_identity():
    assert MatAdd.identity == GenericZeroMatrix()
    assert MatAdd.identity != S.Zero
