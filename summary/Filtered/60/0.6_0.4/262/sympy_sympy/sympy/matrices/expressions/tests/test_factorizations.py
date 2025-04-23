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
    Tests the QR decomposition of a matrix X.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into Q and R.
    
    Returns:
    None: This function does not return any value. It asserts the correctness of the QR decomposition.
    
    Assertions:
    - The shapes of Q_ and R should match the shape of the input matrix X.
    - Q_ should be an orthogonal matrix.
    - R should be an upper triangular matrix.
    """

    Q_, R = qr(X)
    assert Q_.shape == R.shape == X.shape
    assert ask(Q.orthogonal(Q_))
    assert ask(Q.upper_triangular(R))

def test_svd():
    """
    Performs Singular Value Decomposition (SVD) on a given matrix X.
    
    This function computes the SVD of the input matrix X and checks the properties of the resulting matrices.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (numpy.ndarray): The left singular vectors.
    S (numpy.ndarray): The singular values.
    V (numpy.ndarray): The right singular vectors.
    
    Assertions:
    - The shapes of U, S, V, and
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
assert ask(Q.diagonal(S))
