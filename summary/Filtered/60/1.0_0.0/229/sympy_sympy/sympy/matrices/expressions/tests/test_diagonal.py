from sympy.matrices.expressions import MatrixSymbol
from sympy.matrices.expressions.diagonal import DiagonalMatrix, DiagonalOf
from sympy import Symbol, ask, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)
D = DiagonalMatrix(X)
d = DiagonalOf(X)

def test_DiagonalMatrix():
    """
    Test the DiagonalMatrix function.
    
    This function checks the properties of a DiagonalMatrix, including its shape, diagonal elements, and behavior with symbolic indices.
    
    Parameters:
    - D: The DiagonalMatrix to be tested.
    - n: The size of the matrix.
    - X: The input matrix from which the diagonal matrix is created.
    
    Returns:
    - None: This function does not return any value. It asserts conditions to test the DiagonalMatrix.
    
    Key Points:
    - The shape of the Diagonal
    """

    assert D.shape == (n, n)
    assert D[1, 2] == 0
    assert D[1, 1] == X[1, 1]
    i = Symbol('i')
    j = Symbol('j')
    x = MatrixSymbol('x', 3, 3)
    ij = DiagonalMatrix(x)[i, j]
    assert ij != 0
    assert ij.subs({i:0, j:0}) == x[0, 0]
    assert ij.subs({i:0, j:1}) == 0
    assert ij.subs({i:1, j:1}) == x[1, 1]

def test_DiagonalMatrix_Assumptions():
    assert ask(Q.diagonal(D))

def test_DiagonalOf():
    assert d.shape == (n, 1)
    assert d[2, 0] == X[2, 2]
