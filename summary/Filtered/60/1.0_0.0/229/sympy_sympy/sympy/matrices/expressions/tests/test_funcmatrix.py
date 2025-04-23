from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements i - j. The matrix is represented as a FunctionMatrix, and the elements are defined by the lambda function i - j. The matrix can be used in matrix operations such as addition and multiplication.
    
    Parameters:
    None
    
    Returns:
    X (FunctionMatrix): A 3x3 matrix with elements i - j.
    
    Attributes:
    - X[1, 1] (int): The element at the second row and second column is 0.
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
