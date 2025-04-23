from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements defined by the lambda function i - j. The matrix is a symbolic expression and can be used in matrix operations.
    
    Parameters:
    i, j (Symbols): The row and column indices of the matrix elements.
    
    Returns:
    FunctionMatrix: A 3x3 matrix with elements defined by the lambda function i - j.
    
    Attributes:
    shape (tuple): The shape of the matrix, which is (3, 3).
    rows (int): The number of rows
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
