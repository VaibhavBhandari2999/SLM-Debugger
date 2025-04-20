from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements as the difference between row and column indices. The matrix is represented as a FunctionMatrix with a Lambda function that computes the value at each position (i, j) as i - j. The matrix is then converted to a sympy Matrix and basic matrix operations are demonstrated.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Attributes:
    - X: A 3x3 FunctionMatrix with elements i - j.
    - X[1, 1
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
