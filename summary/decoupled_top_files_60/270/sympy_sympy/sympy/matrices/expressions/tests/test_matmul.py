from sympy.core import I, symbols, Basic, Mul, S
from sympy.functions import adjoint, transpose
from sympy.matrices import (Identity, Inverse, Matrix, MatrixSymbol, ZeroMatrix,
        eye, ImmutableMatrix)
from sympy.matrices.expressions import Adjoint, Transpose, det, MatPow
from sympy.matrices.expressions.matexpr import GenericIdentity
from sympy.matrices.expressions.matmul import (factor_in_front, remove_ids,
        MatMul, combine_powers, any_zeros, unpack, only_squares)
from sympy.strategies import null_safe
from sympy import refine, Q, Symbol

from sympy.testing.pytest import XFAIL

n, m, l, k = symbols('n m l k', integer=True)
x = symbols('x')
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)


def test_adjoint():
    """
    Test the adjoint operation for matrices and matrix expressions.
    
    This function checks the adjoint operation for matrix multiplication and scalar multiplication.
    It also verifies the adjoint of a matrix and the adjoint of a matrix multiplied by a scalar.
    
    Parameters:
    - A, B: Matrices or matrix expressions for which the adjoint operation is tested.
    - M: A matrix for which the adjoint is calculated and verified.
    
    Returns:
    - None: The function asserts the correctness of the adjoint operation without returning any
    """

    assert adjoint(A*B) == Adjoint(B)*Adjoint(A)
    assert adjoint(2*A*B) == 2*Adjoint(B)*Adjoint(A)
    assert adjoint(2*I*C) == -2*I*Adjoint(C)

    M = Matrix(2, 2, [1, 2 + I, 3, 4])
    MA = Matrix(2, 2, [1, 3, 2 - I, 4])
    assert adjoint(M) == MA
    assert adjoint(2*M) == 2*MA
    assert adjoint(MatMul(2, M)) == MatMul(2, MA).doit()


def test_transpose():
    assert transpose(A*B) == Transpose(B)*Transpose(A)
    assert transpose(2*A*B) == 2*Transpose(B)*Transpose(A)
    assert transpose(2*I*C) == 2*I*Transpose(C)

    M = Matrix(2, 2, [1, 2 + I, 3, 4])
    MT = Matrix(2, 2, [1, 3, 2 + I, 4])
    assert transpose(M) == MT
    assert transpose(2*M) == 2*MT
    assert transpose(x*M) == x*MT
    assert transpose(MatMul(2, M)) == MatMul(2, MT).doit()


def test_factor_in_front():
    assert factor_in_front(MatMul(A, 2, B, evaluate=False)) ==\
                           MatMul(2, A, B, evaluate=False)


def test_remove_ids():
    """
    Remove identity matrices from the expression.
    
    This function takes a matrix expression and removes any identity matrices
    that are either multiplied by other matrices or are standalone.
    
    Parameters:
    expr (MatrixExpression): The matrix expression from which to remove identity matrices.
    
    Returns:
    MatrixExpression: The simplified matrix expression with identity matrices removed.
    
    Examples:
    >>> from sympy.matrices.expressions import MatMul, Identity
    >>> from sympy.abc import m, n
    >>> from sympy.matrices.ex
    """

    assert remove_ids(MatMul(A, Identity(m), B, evaluate=False)) == \
                      MatMul(A, B, evaluate=False)
    assert null_safe(remove_ids)(MatMul(Identity(n), evaluate=False)) == \
                                 MatMul(Identity(n), evaluate=False)


def test_combine_powers():
    assert combine_powers(MatMul(D, Inverse(D), D, evaluate=False)) == \
                 MatMul(Identity(n), D, evaluate=False)


def test_any_zeros():
    assert any_zeros(MatMul(A, ZeroMatrix(m, k), evaluate=False)) == \
                     ZeroMatrix(n, k)


def test_unpack():
    assert unpack(MatMul(A, evaluate=False)) == A
    x = MatMul(A, B)
    assert unpack(x) == x


def test_only_squares():
    """
    Generate a list of matrices that are squares.
    
    This function takes one or more matrices as input and returns a list
    containing only the matrices that are square (i.e., have the same number
    of rows and columns).
    
    Parameters:
    *matrices: Variable number of matrix arguments (2D numpy arrays or
    objects that can be converted to 2D numpy arrays).
    
    Returns:
    list: A list of matrices that are squares.
    
    Examples:
    >>> only_squares(C)
    """

    assert only_squares(C) == [C]
    assert only_squares(C, D) == [C, D]
    assert only_squares(C, A, A.T, D) == [C, A*A.T, D]


def test_determinant():
    assert det(2*C) == 2**n*det(C)
    assert det(2*C*D) == 2**n*det(C)*det(D)
    assert det(3*C*A*A.T*D) == 3**n*det(C)*det(A*A.T)*det(D)


def test_doit():
    assert MatMul(C, 2, D).args == (C, 2, D)
    assert MatMul(C, 2, D).doit().args == (2, C, D)
    assert MatMul(C, Transpose(D*C)).args == (C, Transpose(D*C))
    assert MatMul(C, Transpose(D*C)).doit(deep=True).args == (C, C.T, D.T)


def test_doit_drills_down():
    """
    Perform matrix multiplication and exponentiation.
    
    This function evaluates the matrix multiplication of `X` and the square of `Y`.
    It also evaluates the matrix multiplication of `C` and the transpose of the product of `D` and `C`.
    
    Parameters:
    - X (ImmutableMatrix): The first matrix.
    - Y (ImmutableMatrix): The second matrix to be squared before multiplication.
    
    Returns:
    - ImmutableMatrix: The result of the matrix multiplication X * Y**2.
    
    Example:
    >>> X = ImmutableMatrix
    """

    X = ImmutableMatrix([[1, 2], [3, 4]])
    Y = ImmutableMatrix([[2, 3], [4, 5]])
    assert MatMul(X, MatPow(Y, 2)).doit() == X*Y**2
    assert MatMul(C, Transpose(D*C)).doit().args == (C, C.T, D.T)


def test_doit_deep_false_still_canonical():
    assert (MatMul(C, Transpose(D*C), 2).doit(deep=False).args ==
            (2, C, Transpose(D*C)))


def test_matmul_scalar_Matrix_doit():
    # Issue 9053
    X = Matrix([[1, 2], [3, 4]])
    assert MatMul(2, X).doit() == 2*X


def test_matmul_sympify():
    assert isinstance(MatMul(eye(1), eye(1)).args[0], Basic)


def test_collapse_MatrixBase():
    A = Matrix([[1, 1], [1, 1]])
    B = Matrix([[1, 2], [3, 4]])
    assert MatMul(A, B).doit() == ImmutableMatrix([[4, 6], [4, 6]])


def test_refine():
    """
    Refine and simplify matrix expressions involving orthogonal matrices.
    
    This function simplifies matrix expressions by applying properties of orthogonal matrices.
    Key parameters:
    - `expr`: The matrix expression to be refined.
    - `Q`: The orthogonal matrix involved in the expression.
    
    Key keywords:
    - `doit`: If `True`, the function will attempt to simplify the expression further.
    
    The function supports the following operations:
    - Simplifying expressions involving the product of a matrix and its transpose with an orthogonal matrix.
    - Simplifying expressions
    """

    assert refine(C*C.T*D, Q.orthogonal(C)).doit() == D

    kC = k*C
    assert refine(kC*C.T, Q.orthogonal(C)).doit() == k*Identity(n)
    assert refine(kC* kC.T, Q.orthogonal(C)).doit() == (k**2)*Identity(n)

def test_matmul_no_matrices():
    assert MatMul(1) == 1
    assert MatMul(n, m) == n*m
    assert not isinstance(MatMul(n, m), MatMul)

def test_matmul_args_cnc():
    assert MatMul(n, A, A.T).args_cnc() == [[n], [A, A.T]]
    assert MatMul(A, A.T).args_cnc() == [[], [A, A.T]]

@XFAIL
def test_matmul_args_cnc_symbols():
    # Not currently supported
    a, b = symbols('a b', commutative=False)
    assert MatMul(n, a, b, A, A.T).args_cnc() == [[n], [a, b, A, A.T]]
    assert MatMul(n, a, A, b, A.T).args_cnc() == [[n], [a, A, b, A.T]]

def test_issue_12950():
    M = Matrix([[Symbol("x")]]) * MatrixSymbol("A", 1, 1)
    assert MatrixSymbol("A", 1, 1).as_explicit()[0]*Symbol('x') == M.as_explicit()[0]

def test_construction_with_Mul():
    assert Mul(C, D) == MatMul(C, D)
    assert Mul(D, C) == MatMul(D, C)

def test_generic_identity():
    assert MatMul.identity == GenericIdentity()
    assert MatMul.identity != S.One
