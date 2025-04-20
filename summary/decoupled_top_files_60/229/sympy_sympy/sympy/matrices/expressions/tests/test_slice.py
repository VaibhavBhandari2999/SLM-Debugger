from sympy.matrices.expressions.slice import MatrixSlice
from sympy.matrices.expressions import MatrixSymbol
from sympy.abc import a, b, c, d, k, l, m, n
from sympy.utilities.pytest import raises, XFAIL
from sympy.functions.elementary.integers import floor
from sympy.assumptions import assuming, Q


X = MatrixSymbol('X', n, m)
Y = MatrixSymbol('Y', m, k)

def test_shape():
    B = MatrixSlice(X, (a, b), (c, d))
    assert B.shape == (b - a, d - c)

def test_entry():
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
    
    This function verifies that slicing operations on a matrix `X` produce the expected results. It checks for correctness in slicing with specific start and stop indices, as well as slicing with step values and full axes.
    
    Parameters:
    None (the function uses a hypothetical matrix `X` defined elsewhere)
    
    Returns:
    None (the function asserts the correctness of slicing operations)
    
    Key Assertions:
    - Slicing with specific start and stop indices: X[1:5,
    """

    assert X[1:5, 2:4] == MatrixSlice(X, (1, 5), (2, 4))
    assert X[1, 2:4] == MatrixSlice(X, 1, (2, 4))
    assert X[1:5, :].shape == (4, X.shape[1])
    assert X[:, 1:5].shape == (X.shape[0], 4)

    assert X[::2, ::2].shape == (floor(n/2), floor(m/2))
    assert X[2, :] == MatrixSlice(X, 2, (0, m))
    assert X[k, :] == MatrixSlice(X, k, (0, m))

def test_exceptions():
    """
    Test exceptions for MatrixSymbol.
    
    Parameters:
    X (MatrixSymbol): A matrix symbol with dimensions 10x20.
    
    Raises:
    IndexError: If slicing is out of bounds.
    
    Examples:
    >>> X = MatrixSymbol('x', 10, 20)
    >>> test_exceptions()
    # The function will raise IndexError for the specified slicing conditions.
    """

    X = MatrixSymbol('x', 10, 20)
    raises(IndexError, lambda: X[0:12, 2])
    raises(IndexError, lambda: X[0:9, 22])
    raises(IndexError, lambda: X[-1:5, 2])

@XFAIL
def test_symmetry():
    """
    Test the symmetry of a matrix.
    
    Parameters:
    X (MatrixSymbol): A 10x10 symbolic matrix.
    
    Returns:
    The transposed submatrix Y (X[:5, 5:]) is equal to the submatrix X[5:, :5] under the assumption that X is symmetric.
    
    Assumptions:
    - X is a symmetric matrix.
    
    Example:
    Given a symmetric matrix X, the function verifies that the transposed submatrix Y (X[:5, 5:]) is equal
    """

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
