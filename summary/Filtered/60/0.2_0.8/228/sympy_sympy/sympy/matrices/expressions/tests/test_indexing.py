from sympy import (symbols, MatrixSymbol, MatPow, BlockMatrix,
        Identity, ZeroMatrix, ImmutableMatrix, eye, Sum)
from sympy.utilities.pytest import raises

k, l, m, n = symbols('k l m n', integer=True)
i, j = symbols('i j', integer=True)

W = MatrixSymbol('W', k, l)
X = MatrixSymbol('X', l, m)
Y = MatrixSymbol('Y', l, m)
Z = MatrixSymbol('Z', m, n)

A = MatrixSymbol('A', 2, 2)
B = MatrixSymbol('B', 2, 2)
x = MatrixSymbol('x', 1, 2)
y = MatrixSymbol('x', 2, 1)


def test_symbolic_indexing():
    x12 = X[1, 2]
    assert all(s in str(x12) for s in ['1', '2', X.name])
    # We don't care about the exact form of this.  We do want to make sure
    # that all of these features are present


def test_add_index():
    assert (X + Y)[i, j] == X[i, j] + Y[i, j]


def test_mul_index():
    """
    Test multiplication and indexing of matrices.
    
    This function checks the multiplication and indexing of matrices A, B, and Y.
    It also tests the multiplication of mutable matrices and the summation of elements
    in the resulting matrix.
    
    Parameters:
    A (Matrix): The first matrix.
    B (Matrix): The second matrix.
    y (Matrix): The second matrix used for indexing.
    
    Returns:
    None: This function does not return any value. It asserts the correctness of the operations.
    
    Key Points:
    1. Asserts that
    """

    assert (A*y)[0, 0] == A[0, 0]*y[0, 0] + A[0, 1]*y[1, 0]
    assert (A*B).as_mutable() == (A.as_mutable() * B.as_mutable())
    X = MatrixSymbol('X', n, m)
    Y = MatrixSymbol('Y', m, k)

    result = (X*Y)[4,2]
    expected = Sum(X[4, i]*Y[i, 2], (i, 0, m - 1))
    assert result.args[0].dummy_eq(expected.args[0], i)
    assert result.args[1][1:] == expected.args[1][1:]


def test_pow_index():
    Q = MatPow(A, 2)
    assert Q[0, 0] == A[0, 0]**2 + A[0, 1]*A[1, 0]


def test_transpose_index():
    assert X.T[i, j] == X[j, i]


def test_Identity_index():
    """
    Test the identity matrix indexing.
    
    Parameters:
    I (Identity): The identity matrix object of size 3.
    
    Returns:
    None
    
    Assertions:
    - The diagonal elements I[0, 0], I[1, 1], and I[2, 2] are equal to 1.
    - The off-diagonal elements I[1, 0], I[0, 1], and I[2, 1] are equal to 0.
    - An
    """

    I = Identity(3)
    assert I[0, 0] == I[1, 1] == I[2, 2] == 1
    assert I[1, 0] == I[0, 1] == I[2, 1] == 0
    raises(IndexError, lambda: I[3, 3])


def test_block_index():
    I = Identity(3)
    Z = ZeroMatrix(3, 3)
    B = BlockMatrix([[I, I], [I, I]])
    e3 = ImmutableMatrix(eye(3))
    BB = BlockMatrix([[e3, e3], [e3, e3]])
    assert B[0, 0] == B[3, 0] == B[0, 3] == B[3, 3] == 1
    assert B[4, 3] == B[5, 1] == 0

    BB = BlockMatrix([[e3, e3], [e3, e3]])
    assert B.as_explicit() == BB.as_explicit()

    BI = BlockMatrix([[I, Z], [Z, I]])

    assert BI.as_explicit().equals(eye(6))


def test_slicing():
    A.as_explicit()[0, :]  # does not raise an error


def test_errors():
    raises(IndexError, lambda: Identity(2)[1, 2, 3, 4, 5])
    raises(IndexError, lambda: Identity(2)[[1, 2, 3, 4, 5]])
