from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 FunctionMatrix with elements defined by the lambda function i - j. The matrix elements are evaluated using the given symbols i and j. The matrix is then used to demonstrate basic matrix operations and properties.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Attributes:
    - X: A 3x3 FunctionMatrix with elements defined by the lambda function i - j.
    - X[1, 1]: The element at the second row and second column of the matrix, which
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
