from sympy.core import I, symbols, Basic
from sympy.functions import adjoint, transpose
from sympy.matrices import (Identity, Inverse, Matrix, MatrixSymbol, ZeroMatrix,
        eye, ImmutableMatrix)
from sympy.matrices.expressions import Adjoint, Transpose, det, MatPow
from sympy.matrices.expressions.matmul import (factor_in_front, remove_ids,
        MatMul, xxinv, any_zeros, unpack, only_squares)
from sympy.strategies import null_safe
from sympy import refine, Q, Symbol

n, m, l, k = symbols('n m l k', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)


def test_adjoint():
    """
    Test the adjoint operation for matrices and matrix expressions.
    
    This function checks the adjoint operation for different matrix expressions
    and verifies that the adjoint of a product of matrices is the product of the
    adjoints in reverse order, and that the adjoint of a scalar multiple of a
    matrix is the scalar multiple of the adjoint of the matrix.
    
    Parameters:
    - A, B, C (Matrix): Matrices for which the adjoint operation is tested.
    - I (Identity Matrix): Identity
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
    assert transpose(MatMul(2, M)) == MatMul(2, MT).doit()


def test_factor_in_front():
    assert factor_in_front(MatMul(A, 2, B, evaluate=False)) ==\
                           MatMul(2, A, B, evaluate=False)


def test_remove_ids():
    assert remove_ids(MatMul(A, Identity(m), B, evaluate=False)) == \
                      MatMul(A, B, evaluate=False)
    assert null_safe(remove_ids)(MatMul(Identity(n), evaluate=False)) == \
                                 MatMul(Identity(n), evaluate=False)


def test_xxinv():
    assert xxinv(MatMul(D, Inverse(D), D, evaluate=False)) == \
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
    
    Parameters:
    *args (numpy.ndarray): A variable number of 2D numpy arrays.
    
    Returns:
    list: A list of input arrays that are square matrices (i.e., have the same number of rows and columns).
    
    Examples:
    >>> only_squares(np.array([[1, 2], [3, 4]]))
    [array([[1, 2],
    [3, 4]])]
    >>> only_squares(np
    """

    assert only_squares(C) == [C]
    assert only_squares(C, D) == [C, D]
    assert only_squares(C, A, A.T, D) == [C, A*A.T, D]


def test_determinant():
    assert det(2*C) == 2**n*det(C)
    assert det(2*C*D) == 2**n*det(C)*det(D)
    assert det(3*C*A*A.T*D) == 3**n*det(C)*det(A*A.T)*det(D)


def test_doit():
    """
    Test the `doit` method for the `MatMul` class.
    
    This function checks the behavior of the `doit` method for the `MatMul` class. It verifies that the `doit` method correctly handles scalar multiplication and transposition within matrix multiplication expressions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The `doit` method is called on a `MatMul` object with arguments (C, 2, D) and checks if the result
    """

    assert MatMul(C, 2, D).args == (C, 2, D)
    assert MatMul(C, 2, D).doit().args == (2, C, D)
    assert MatMul(C, Transpose(D*C)).args == (C, Transpose(D*C))
    assert MatMul(C, Transpose(D*C)).doit(deep=True).args == (C, C.T, D.T)


def test_doit_drills_down():
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
    """
    Collapse the result of matrix multiplication of two matrices.
    
    Parameters:
    A (Matrix): The first matrix.
    B (Matrix): The second matrix.
    
    Returns:
    ImmutableMatrix: The result of matrix multiplication of A and B.
    
    Example:
    >>> A = Matrix([[1, 1], [1, 1]])
    >>> B = Matrix([[1, 2], [3, 4]])
    >>> test_collapse_MatrixBase(A, B)
    ImmutableMatrix([[4, 6], [4, 6
    """

    A = Matrix([[1, 1], [1, 1]])
    B = Matrix([[1, 2], [3, 4]])
    assert MatMul(A, B).doit() == ImmutableMatrix([[4, 6], [4, 6]])


def test_refine():
    assert refine(C*C.T*D, Q.orthogonal(C)).doit() == D

    kC = k*C
    assert refine(kC*C.T, Q.orthogonal(C)).doit() == k*Identity(n)
    assert refine(kC* kC.T, Q.orthogonal(C)).doit() == (k**2)*Identity(n)

def test_matmul_no_matrices():
    """
    MatMul(n, m)
    
    Parameters:
    n (int): The first number to multiply.
    m (int): The second number to multiply.
    
    Returns:
    int: The result of multiplying n and m.
    
    Note:
    - If only one argument is provided, it is treated as n and m is assumed to be 1.
    - The result is not an instance of MatMul.
    - MatMul is not a matrix multiplication operation but a simple multiplication function.
    """

    assert MatMul(1) == 1
    assert MatMul(n, m) == n*m
    assert not isinstance(MatMul(n, m), MatMul)

def test_matmul_args_cnc():
    a, b = symbols('a b', commutative=False)
    assert MatMul(n, a, b, A, A.T).args_cnc() == ([n], [a, b, A, A.T])
    assert MatMul(A, A.T).args_cnc() == ([1], [A, A.T])

def test_issue_12950():
    M = Matrix([[Symbol("x")]]) * MatrixSymbol("A", 1, 1)
    assert MatrixSymbol("A", 1, 1).as_explicit()[0]*Symbol('x') == M.as_explicit()[0]
