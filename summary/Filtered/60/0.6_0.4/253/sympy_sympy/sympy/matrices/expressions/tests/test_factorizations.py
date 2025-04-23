from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    This function performs LU decomposition on the input matrix `X` and checks the validity of the resulting lower triangular matrix `L` and upper triangular matrix `U`.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into L and U.
    
    Returns:
    L (numpy.ndarray): The lower triangular matrix obtained from the LU decomposition.
    U (numpy.ndarray): The upper triangular matrix obtained from the LU decomposition.
    
    Assertions:
    - The shapes
    """

    L, U = lu(X)
    assert L.shape == U.shape == X.shape
    assert ask(Q.lower_triangular(L))
    assert ask(Q.upper_triangular(U))

def test_Cholesky():
    L = LofCholesky(X)

def test_QR():
    Q_, R = qr(X)
    assert Q_.shape == R.shape == X.shape
    assert ask(Q.orthogonal(Q_))
    assert ask(Q.upper_triangular(R))

def test_svd():
    """
    Performs Singular Value Decomposition (SVD) on a matrix X.
    
    This function computes the SVD of a given matrix X, returning the matrices U, S, and V such that X = U * diag(S) * V^T.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (numpy.ndarray): The left singular vectors of X.
    S (numpy.ndarray): The singular values of X, represented as a 1D array
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
