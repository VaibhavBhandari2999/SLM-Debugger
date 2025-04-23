from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements defined by the lambda function i - j. The matrix is a symbolic matrix expression and supports matrix operations.
    
    Parameters:
    - None
    
    Returns:
    - A 3x3 symbolic matrix with elements i - j, where i and j are the row and column indices, respectively.
    
    Attributes:
    - X[1, 1]: The element at the second row and second column, which is 0.
    - X[1, 2]: The element at
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
