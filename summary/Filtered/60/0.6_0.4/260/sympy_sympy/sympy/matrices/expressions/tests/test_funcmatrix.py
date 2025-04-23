from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements as the difference between indices i and j. The matrix is represented as a FunctionMatrix with a Lambda function that computes i - j for each element. The matrix is also converted to a sympy Matrix and the result is checked for equality. The expression X*X + X is also evaluated to ensure it returns a MatrixExpr.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Attributes:
    - i, j: Symbols representing row and column indices
    -
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
