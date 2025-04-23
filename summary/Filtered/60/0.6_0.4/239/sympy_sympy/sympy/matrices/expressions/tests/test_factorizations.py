from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy import Symbol, MatrixSymbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    This function performs LU decomposition on a given matrix `X` and checks the properties of the resulting lower triangular matrix `L` and upper triangular matrix `U`.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into LU form.
    
    Returns:
    L (numpy.ndarray): The lower triangular matrix obtained from the LU decomposition.
    U (numpy.ndarray): The upper triangular matrix obtained from the LU decomposition.
    
    Assertions:
    - The shapes of
    """

    L, U = lu(X)
    assert L.shape == U.shape == X.shape
    assert ask(Q.lower_triangular(L))
    assert ask(Q.upper_triangular(U))

def test_Cholesky():
    L = LofCholesky(X)

def test_QR():
    """
    Generate an orthogonal matrix Q and an upper triangular matrix R from the QR decomposition of a given matrix X.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into QR form.
    
    Returns:
    Q_ (numpy.ndarray): The orthogonal matrix Q.
    R (numpy.ndarray): The upper triangular matrix R.
    
    Assertions:
    - The shapes of Q_ and R are equal and match the shape of the input matrix X.
    - Q_ is an orthogonal matrix.
    -
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
