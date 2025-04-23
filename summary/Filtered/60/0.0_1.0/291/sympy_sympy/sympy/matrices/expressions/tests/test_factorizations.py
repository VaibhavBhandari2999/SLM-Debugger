from sympy.matrices.expressions.factorizations import lu, LofCholesky, qr, svd
from sympy.assumptions.ask import (Q, ask)
from sympy.core.symbol import Symbol
from sympy.matrices.expressions.matexpr import MatrixSymbol

n = Symbol('n')
X = MatrixSymbol('X', n, n)

def test_LU():
    """
    Test the LU decomposition of a matrix.
    
    This function performs LU decomposition on the input matrix `X` and checks if the resulting lower triangular matrix `L` and upper triangular matrix `U` have the correct shapes and properties.
    
    Parameters:
    X (numpy.ndarray): The input matrix to be decomposed into LU form.
    
    Returns:
    L (numpy.ndarray): The lower triangular matrix obtained from the LU decomposition.
    U (numpy.ndarray): The upper triangular matrix obtained from the LU decomposition.
    
    Assertions:
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
    U, S, V = svd(X)
    assert U.shape == S.shape == V.shape == X.shape
    assert ask(Q.orthogonal(U))
    assert ask(Q.orthogonal(V))
    assert ask(Q.diagonal(S))
