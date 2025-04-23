from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    Parameters:
    X (Matrix): The input matrix to be decomposed into lower (L) and upper (U) triangular matrices.
    
    Returns:
    L (Matrix): The lower triangular matrix.
    U (Matrix): The upper triangular matrix.
    
    Asserts:
    - The shapes of L and U are equal and match the shape of the input matrix X.
    - L is a lower triangular matrix.
    - U is an upper triangular matrix.
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
    Performs Singular Value Decomposition (SVD) on a matrix.
    
    This function decomposes a given matrix X into three matrices U, S, and V, such that X = U * S * V^T. The function checks the correctness of the decomposition by verifying the shapes of the matrices and the orthogonality of U and V, as well as the diagonal nature of S.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
