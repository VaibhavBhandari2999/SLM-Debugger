from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 FunctionMatrix with elements defined by the lambda function i - j. The matrix is indexed by symbols i and j. The matrix elements are evaluated as i - j, resulting in a matrix with values [0, -1, -2; 1, 0, -1; 2, 1, 0]. The matrix has a shape of (3, 3) and the number of rows and columns is 3. The result of the matrix
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
