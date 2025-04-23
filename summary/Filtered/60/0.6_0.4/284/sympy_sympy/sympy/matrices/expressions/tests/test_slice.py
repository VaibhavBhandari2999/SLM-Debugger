from sympy.matrices.expressions.slice import MatrixSlice
from sympy.matrices.expressions import MatrixSymbol
from sympy.abc import a, b, c, d, k, l, m, n
from sympy.testing.pytest import raises, XFAIL
from sympy.functions.elementary.integers import floor
from sympy.assumptions import assuming, Q


X = MatrixSymbol('X', n, m)
Y = MatrixSymbol('Y', m, k)

def test_shape():
    B = MatrixSlice(X, (a, b), (c, d))
    assert B.shape == (b - a, d - c)

def test_entry():
    """
    Test the MatrixSlice class for slicing operations on a 2D array X. The function checks the following:
    
    - Create a MatrixSlice object B from X with specified row and column slices (a, b) and (c, d).
    - Verify that B[0,0] is equal to X[a, c].
    - Verify that B[k,l] is equal to X[a+k, c+l].
    - Raise an IndexError when attempting to access an invalid index with MatrixSlice(X, 1
    """

    B = MatrixSlice(X, (a, b), (c, d))
    assert B[0,0] == X[a, c]
    assert B[k,l] == X[a+k, c+l]
    raises(IndexError, lambda : MatrixSlice(X, 1, (2, 5))[1, 0])

    assert X[1::2, :][1, 3] == X[1+2, 3]
    assert X[:, 1::2][3, 1] == X[3, 1+2]

def test_on_diag():
    assert not MatrixSlice(X, (a, b), (c, d)).on_diag
    assert MatrixSlice(X, (a, b), (a, b)).on_diag

def test_inputs():
    assert MatrixSlice(X, 1, (2, 5)) == MatrixSlice(X, (1, 2), (2, 5))
    assert MatrixSlice(X, 1, (2, 5)).shape == (1, 3)

def test_slicing():
    """
    Tests slicing operations on a matrix.
    
    This function checks various slicing operations on a matrix X and ensures that the sliced portions match the expected MatrixSlice objects. It also verifies the shape of slices taken along rows and columns.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations:
    - Slicing a portion of the matrix with specified row and column ranges.
    - Slicing a row or column with a specified range.
    - Verifying the shape of slices taken along rows and columns.
    """

    assert X[1:5, 2:4] == MatrixSlice(X, (1, 5), (2, 4))
    assert X[1, 2:4] == MatrixSlice(X, 1, (2, 4))
    assert X[1:5, :].shape == (4, X.shape[1])
    assert X[:, 1:5].shape == (X.shape[0], 4)

    assert X[::2, ::2].shape == (floor(n/2), floor(m/2))
    assert X[2, :] == MatrixSlice(X, 2, (0, m))
    assert X[k, :] == MatrixSlice(X, k, (0, m))

def test_exceptions():
    X = MatrixSymbol('x', 10, 20)
    raises(IndexError, lambda: X[0:12, 2])
    raises(IndexError, lambda: X[0:9, 22])
    raises(IndexError, lambda: X[-1:5, 2])

@XFAIL
def test_symmetry():
    X = MatrixSymbol('x', 10, 10)
    Y = X[:5, 5:]
    with assuming(Q.symmetric(X)):
        assert Y.T == X[5:, :5]

def test_slice_of_slice():
    """
    Test slicing of slices from a matrix symbol.
    
    Parameters:
    X (MatrixSymbol): A symbolic matrix of dimensions 10x10.
    
    Returns:
    Expr: An expression representing the sliced matrix element or submatrix.
    """

    X = MatrixSymbol('x', 10, 10)
    assert X[2, :][:, 3][0, 0] == X[2, 3]
    assert X[:5, :5][:4, :4] == X[:4, :4]
    assert X[1:5, 2:6][1:3, 2] == X[2:4, 4]
    assert X[1:9:2, 2:6][1:3, 2] == X[3:7:2, 4]

def test_negative_index():
    X = MatrixSymbol('x', 10, 10)
    assert X[-1, :] == X[9, :]
