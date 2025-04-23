from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    This function performs LU decomposition on a given matrix `X` and checks if the resulting matrices `L` and `U` are lower and upper triangular, respectively, and have the same shape as the input matrix.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into L and U.
    
    Returns:
    L (numpy.ndarray): The lower triangular matrix.
    U (numpy.ndarray): The upper triangular matrix.
    
    Raises:
    AssertionError:
    """

    L, U = lu(X)
    assert L.shape == U.shape == X.shape
    assert ask(Q.lower_triangular(L))
    assert ask(Q.upper_triangular(U))

def test_Cholesky():
    L = LofCholesky(X)

def test_QR():
    """
    Tests the QR decomposition of a matrix.
    
    This function performs QR decomposition on a given matrix `X` and checks if the resulting matrices `Q_` and `R` satisfy certain properties.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into QR form.
    
    Returns:
    None: This function does not return any value. It performs assertions to check the correctness of the QR decomposition.
    
    Assertions:
    - `Q_.shape == R.shape == X.shape`: The shapes of
    """

    Q_, R = qr(X)
    assert Q_.shape == R.shape == X.shape
    assert ask(Q.orthogonal(Q_))
    assert ask(Q.upper_triangular(R))

def test_svd():
    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
