from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Generate a 3x3 matrix with elements i - j. The matrix is represented as a FunctionMatrix, and the function returns the matrix.
    
    Parameters:
    None
    
    Returns:
    FunctionMatrix: A 3x3 matrix with elements i - j.
    
    Attributes:
    X (FunctionMatrix): The generated 3x3 matrix.
    i, j (symbols): The symbols used to define the matrix elements.
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
