from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements i - j. The matrix is represented as a FunctionMatrix with a Lambda function defining the element at position (i, j). The function also demonstrates basic matrix operations such as addition and multiplication with itself.
    
    Parameters:
    None
    
    Returns:
    None
    
    Attributes:
    X (FunctionMatrix): A 3x3 matrix with elements i - j.
    
    Methods:
    - X[1, 1]: Returns the element at position (1, 1).
    - X
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
