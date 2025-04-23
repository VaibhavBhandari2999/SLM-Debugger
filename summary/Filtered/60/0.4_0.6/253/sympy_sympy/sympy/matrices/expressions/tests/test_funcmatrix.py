from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements i - j. The matrix is a symbolic matrix with elements defined by the lambda function i - j. The matrix is named X and its elements can be accessed using the indices [i, j]. The shape of the matrix is (3, 3) and the number of rows and columns is 3. The matrix can be converted to a sympy Matrix object using the Matrix() function. The matrix can also be used in matrix operations such as
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
