from sympy.core import I, symbols, Basic, Mul, S
from sympy.core.mul import mul
from sympy.functions import adjoint, transpose
from sympy.matrices import (Identity, Inverse, Matrix, MatrixSymbol, ZeroMatrix,
        eye, ImmutableMatrix)
from sympy.matrices.expressions import Adjoint, Transpose, det, MatPow
from sympy.matrices.expressions.special import GenericIdentity
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

def test_evaluate():
    assert MatMul(C, C, evaluate=True) == MatMul(C, C).doit()

def test_adjoint():
    """
    Test the adjoint operation for matrices and matrix expressions.
    
    This function checks the adjoint operation for different matrix expressions
    and verifies the correctness of the adjoint calculation. It supports scalar
    multiplication and the identity matrix.
    
    Parameters:
    - A, B, C: Matrices or matrix expressions for which the adjoint operation
    is to be tested.
    
    Returns:
    - None: The function asserts the correctness of the adjoint operation
    and does not return any value. If any assertion fails,
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
    Generate a list of matrices that are only the square matrices from the given list.
    
    Parameters:
    *matrices (list of np.ndarray): Variable length argument list of 2D numpy arrays.
    
    Returns:
    list of np.ndarray: A list containing only the square matrices (i.e., matrices with the same number of rows and columns) from the input list.
    
    Examples:
    >>> only_squares(C)
    [C]
    >>> only_squares(C, D)
    [C, D
    """

    assert only_squares(C) == [C]
    assert only_squares(C, D) == [C, D]
    assert only_squares(C, A, A.T, D) == [C, A*A.T, D]


def test_determinant():
    """
    Test the determinant of a matrix after scaling and multiplying with other matrices.
    
    Parameters:
    C (np.ndarray): A square matrix.
    A (np.ndarray): Another square matrix.
    D (np.ndarray): A third square matrix.
    
    Returns:
    bool: True if the determinant properties hold, False otherwise.
    
    This function checks the determinant properties for scaled and multiplied matrices.
    It verifies if the determinant of a scaled matrix is equal to the scalar raised to the power of the matrix dimension times the determinant of
    """

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
    
    This function evaluates the product of a matrix `X` and the square of another matrix `Y`.
    It also checks the multiplication of a constant `C` with the transpose of the product of `D` and `C`.
    
    Parameters:
    - X (ImmutableMatrix): The first matrix.
    - Y (ImmutableMatrix): The second matrix to be squared and then multiplied with `X`.
    
    Returns:
    - ImmutableMatrix: The result of `X * Y**2`.
    
    Example
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

def test_construction_with_mul():
    """
    Test the construction of a matrix multiplication operation.
    
    This function checks the creation of a matrix multiplication operation using the `mul` function. It ensures that the order of matrices in multiplication matters and that the resulting operation is correctly represented by the `MatMul` class.
    
    Parameters:
    C (Matrix): The first matrix in the multiplication.
    D (Matrix): The second matrix in the multiplication.
    
    Returns:
    MatMul: The matrix multiplication operation.
    
    Note:
    - `mul(C, D)`
    """

    assert mul(C, D) == MatMul(C, D)
    assert mul(D, C) == MatMul(D, C)
    assert mul(C, D) != MatMul(D, C)

def test_generic_identity():
    assert MatMul.identity == GenericIdentity()
    assert MatMul.identity != S.One
