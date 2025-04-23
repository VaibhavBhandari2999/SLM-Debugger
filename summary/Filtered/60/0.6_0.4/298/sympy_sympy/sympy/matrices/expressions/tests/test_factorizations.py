from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy.assumptions.ask import (Q, ask)
from sympy.core.symbol import Symbol
from sympy.matrices.expressions.matexpr import MatrixSymbol

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    This function performs LU decomposition on a given matrix X and checks the properties of the resulting lower (L) and upper (U) triangular matrices.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into L and U.
    
    Returns:
    L (numpy.ndarray): The lower triangular matrix.
    U (numpy.ndarray): The upper triangular matrix.
    
    Raises:
    AssertionError: If the shapes of L and U do not match the shape of X
    """

    L, U = lu(X)
    assert L.shape == U.shape == X.shape
    assert ask(Q.lower_triangular(L))
    assert ask(Q.upper_triangular(U))

def test_Cholesky():
    LofCholesky(X)

def test_QR():
    Q_, R = qr(X)
    assert Q_.shape == R.shape == X.shape
    assert ask(Q.orthogonal(Q_))
    assert ask(Q.upper_triangular(R))

def test_svd():
    """
    Performs Singular Value Decomposition (SVD) on a matrix X.
    
    This function decomposes the input matrix X into three matrices: U, S, and V.
    The matrix X is decomposed such that X = U * S * V^T.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed.
    
    Returns:
    U (numpy.ndarray): The left singular vectors of X.
    S (numpy.ndarray): The singular values of X, represented as a 1
    """

    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
