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
    LofCholesky(X)

def test_QR():
    """
    Tests the QR decomposition of a matrix.
    
    This function performs QR decomposition on a given matrix `X` and checks the properties of the resulting matrices `Q_` and `R`.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into QR.
    
    Returns:
    None: This function does not return any value. It performs assertions to validate the properties of the QR decomposition.
    
    Assertions:
    - `Q_.shape == R.shape == X.shape`: The shapes of the orthogonal matrix
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
