from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements i - j. The matrix is represented as a FunctionMatrix with symbolic indices i and j. The function evaluates the matrix at specific positions and checks its shape, rows, and columns. It also verifies that the matrix can be converted to a standard Matrix and that certain matrix operations are supported.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Attributes:
    - X: A 3x3 FunctionMatrix with elements i - j.
    - i, j:
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
