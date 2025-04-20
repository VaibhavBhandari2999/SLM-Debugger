from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 matrix with elements defined by the lambda function i - j.
    
    This function generates a 3x3 matrix where each element is defined by the lambda function i - j. The matrix is a FunctionMatrix object, which is a subclass of MatrixExpr.
    
    Parameters:
    None
    
    Returns:
    X (FunctionMatrix): A 3x3 matrix with elements defined by i - j.
    
    Attributes:
    - X[1, 1]: The element at the second row and second column
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
