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
    The input matrix to be decomposed into lower (L) and upper (U) triangular matrices.
    
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
    LofCholesky(X)

def test_QR():
    """
    Tests the QR decomposition of a matrix X.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into Q and R.
    
    Returns:
    None: This function does not return any value. It asserts that the output matrices Q and R are orthogonal and upper triangular, respectively, and have the same shape as the input matrix X.
    
    Notes:
    - The function uses the `qr` function from a linear algebra library to perform the QR decomposition.
    - The function checks that the
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
