from sympy import (symbols, FunctionMatrix, MatrixExpr, Lambda, Matrix)


def test_funcmatrix():
    """
    Create a 3x3 function matrix with elements defined as i - j.
    
    This function generates a 3x3 matrix where each element is defined by the
    expression i - j. The matrix is created using the `FunctionMatrix` class and
    the `Lambda` function to specify the element expression.
    
    Parameters:
    No parameters.
    
    Returns:
    A 3x3 `FunctionMatrix` object with elements defined as i - j.
    
    Attributes:
    - X[1, 1]: The element at
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
