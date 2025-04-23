from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 FunctionMatrix with elements defined by the lambda function i - j. The matrix is indexed by symbolic variables i and j. The matrix is tested for specific elements and its shape. The matrix multiplication and addition operations are also tested.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Elements:
    - i, j: Symbolic variables used for indexing the matrix.
    - X: A 3x3 FunctionMatrix with elements defined by the lambda function i - j.
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
