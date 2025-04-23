from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
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
    
    This function computes the SVD of a given matrix X, returning the matrices U, S, and V such that X = U * diag(S) * V.T.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (numpy.ndarray): The left singular vectors.
    S (numpy.ndarray): The singular values.
    V (numpy.ndarray): The right singular vectors.
    
    Assertions
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
