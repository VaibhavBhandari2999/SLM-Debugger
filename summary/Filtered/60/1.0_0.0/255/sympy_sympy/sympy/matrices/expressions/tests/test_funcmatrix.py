from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements defined by the lambda function i - j. The matrix is represented as a FunctionMatrix object. The function also demonstrates basic operations and properties of the matrix, such as accessing individual elements, checking the shape, and performing matrix multiplication.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Properties and Operations:
    - X[1, 1] == 0
    - X[1, 2] == -1
    - X.shape == (3
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
