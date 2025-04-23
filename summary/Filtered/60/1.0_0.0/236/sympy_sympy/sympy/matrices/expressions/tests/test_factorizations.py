from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    Parameters
    ----------
    X : Matrix
    The matrix to be decomposed into lower (L) and upper (U) triangular matrices.
    
    Returns
    -------
    L : Matrix
    The lower triangular matrix.
    U : Matrix
    The upper triangular matrix.
    
    Raises
    ------
    AssertionError
    If the shapes of L and U do not match the input matrix X or if L and U do not satisfy the properties of lower and upper triangular matrices, respectively.
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
    
    This function performs QR decomposition on a given matrix X and checks the properties of the resulting matrices Q and R.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into Q and R.
    
    Returns:
    None: This function does not return any value. It performs assertions to validate the properties of the QR decomposition.
    
    Assertions:
    - Q_.shape == R.shape == X.shape: The shapes of the orthogonal matrix Q, upper triangular matrix
    """

    Q_, R = qr(X)
    assert Q_.shape == R.shape == X.shape
    assert ask(Q.orthogonal(Q_))
    assert ask(Q.upper_triangular(R))

def test_svd():
    """
    Performs Singular Value Decomposition (SVD) on a matrix X.
    
    This function decomposes the input matrix X into three matrices: U, S, and V.
    The matrix X is decomposed such that X = U * S * V^T, where U and V are orthogonal matrices,
    and S is a diagonal matrix containing the singular values.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (numpy.ndarray): The left singular vectors of
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
