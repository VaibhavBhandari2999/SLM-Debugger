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
    Test the MatrixSlice class for slicing operations.
    
    This function tests the MatrixSlice class to ensure that it correctly slices a matrix and handles indexing. It checks the following:
    - Slicing with specified start and stop indices for both rows and columns.
    - Accessing elements using the slice notation.
    - Handling of invalid indices.
    
    Parameters:
    - X (Matrix): The matrix to be sliced.
    - a, b, c, d (int): The start and stop indices for rows and columns respectively.
    
    Returns:
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
    Test slicing operations on a matrix.
    
    This function tests various slicing operations on a matrix X and checks if the sliced parts match the expected MatrixSlice objects. It also verifies the shape of the sliced matrices.
    
    Parameters:
    X (numpy.ndarray): The input matrix to perform slicing operations on.
    
    Returns:
    None: The function asserts the correctness of the slicing operations and does not return any value.
    
    Key Assertions:
    - Slicing a submatrix from rows 1 to 5 and columns 2 to
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
    X = MatrixSymbol('x', 10, 10)
    assert X[2, :][:, 3][0, 0] == X[2, 3]
    assert X[:5, :5][:4, :4] == X[:4, :4]
    assert X[1:5, 2:6][1:3, 2] == X[2:4, 4]
    assert X[1:9:2, 2:6][1:3, 2] == X[3:7:2, 4]

def test_negative_index():
    X = MatrixSymbol('x', 10, 10)
    assert X[-1, :] == X[9, :]
