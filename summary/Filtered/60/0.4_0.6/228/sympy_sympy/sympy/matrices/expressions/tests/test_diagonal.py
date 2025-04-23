from sympy.matrices.expressions import MatrixSymbol
from sympy.matrices.expressions.diagonal import DiagonalMatrix, DiagonalOf
from sympy import Symbol, ask, Q

n = Symbol('n')
x = MatrixSymbol('x', n, 1)
X = MatrixSymbol('X', n, n)
D = DiagonalMatrix(x)
d = DiagonalOf(X)

def test_DiagonalMatrix():
    """
    Tests the DiagonalMatrix function.
    
    This function checks the properties of a diagonal matrix D generated from a given vector x. The matrix D is of shape (n, n) and should have non-zero elements only on its diagonal, where D[i, i] = x[i, 0].
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The shape of D should be (n, n).
    - Off-diagonal elements D[i, j] for i != j should
    """

    assert D.shape == (n, n)
    assert D[1, 2] == 0
    assert D[1, 1] == x[1, 0]

def test_DiagonalMatrix_Assumptions():
    assert ask(Q.diagonal(D))

def test_DiagonalOf():
    assert d.shape == (n, 1)
    assert d[2, 0] == X[2, 2]
