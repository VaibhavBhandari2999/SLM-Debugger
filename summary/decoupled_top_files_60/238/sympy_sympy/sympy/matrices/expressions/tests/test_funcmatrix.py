from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 FunctionMatrix with elements defined by the lambda function i - j. The matrix is a symbolic matrix where each element is the difference between the row index and the column index. The matrix is square with 3 rows and 3 columns. The matrix can be used in matrix operations, and the specific elements can be accessed using the indices.
    
    Parameters:
    - None
    
    Returns:
    - X (FunctionMatrix): A 3x3 matrix with elements defined by the lambda function i
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
