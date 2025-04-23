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
    Test the DiagonalMatrix function.
    
    This function checks the properties of a diagonal matrix D generated from a given vector x.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Properties:
    - D.shape == (n, n): The matrix D is a square matrix of size n x n.
    - D[1, 2] == 0: Off-diagonal elements are zero.
    - D[1, 1] == x[1, 0]: The diagonal elements
    """

    assert D.shape == (n, n)
    assert D[1, 2] == 0
    assert D[1, 1] == x[1, 0]

def test_DiagonalMatrix_Assumptions():
    assert ask(Q.diagonal(D))

def test_DiagonalOf():
    assert d.shape == (n, 1)
    assert d[2, 0] == X[2, 2]
