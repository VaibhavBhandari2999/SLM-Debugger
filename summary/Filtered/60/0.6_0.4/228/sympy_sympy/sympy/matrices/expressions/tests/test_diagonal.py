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
    
    This function checks if the generated matrix D is of the correct shape (n, n),
    if the off-diagonal elements are zero, and if the diagonal elements match the
    corresponding elements in the input array x.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    D (numpy.ndarray): The generated diagonal matrix.
    n (int): The size of the matrix.
    x (numpy.ndarray): The input array containing diagonal elements.
    """

    assert D.shape == (n, n)
    assert D[1, 2] == 0
    assert D[1, 1] == x[1, 0]

def test_DiagonalMatrix_Assumptions():
    assert ask(Q.diagonal(D))

def test_DiagonalOf():
    assert d.shape == (n, 1)
    assert d[2, 0] == X[2, 2]
