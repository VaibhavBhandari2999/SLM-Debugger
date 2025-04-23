from sympy.core import symbols, Lambda
from sympy.functions import KroneckerDelta
from sympy.matrices import Matrix
from sympy.matrices.expressions import FunctionMatrix, MatrixExpr, Identity
from sympy.utilities.pytest import raises


def test_funcmatrix_creation():
    """
    Test function for creating a FunctionMatrix.
    
    Parameters:
    - i, j, k: Symbols representing indices for the matrix.
    
    Returns:
    - FunctionMatrix: A 2x2 matrix with all elements set to 0.
    - FunctionMatrix: An empty 0x0 matrix with all elements set to 0.
    
    Raises:
    - ValueError: If the dimensions are negative or non-integer.
    - ValueError: If the lambda function does not have the correct number of arguments.
    - ValueError: If the lambda
    """

    i, j, k = symbols('i j k')
    assert FunctionMatrix(2, 2, Lambda((i, j), 0))
    assert FunctionMatrix(0, 0, Lambda((i, j), 0))

    raises(ValueError, lambda: FunctionMatrix(-1, 0, Lambda((i, j), 0)))
    raises(ValueError, lambda: FunctionMatrix(2.0, 0, Lambda((i, j), 0)))
    raises(ValueError, lambda: FunctionMatrix(2j, 0, Lambda((i, j), 0)))
    raises(ValueError, lambda: FunctionMatrix(0, -1, Lambda((i, j), 0)))
    raises(ValueError, lambda: FunctionMatrix(0, 2.0, Lambda((i, j), 0)))
    raises(ValueError, lambda: FunctionMatrix(0, 2j, Lambda((i, j), 0)))

    raises(ValueError, lambda: FunctionMatrix(2, 2, Lambda(i, 0)))
    raises(ValueError, lambda: FunctionMatrix(2, 2, lambda i, j: 0))
    raises(ValueError, lambda: FunctionMatrix(2, 2, Lambda((i,), 0)))
    raises(ValueError, lambda: FunctionMatrix(2, 2, Lambda((i, j, k), 0)))
    raises(ValueError, lambda: FunctionMatrix(2, 2, i+j))
    assert FunctionMatrix(2, 2, "lambda i, j: 0") == \
        FunctionMatrix(2, 2, Lambda((i, j), 0))

    assert FunctionMatrix(2, 2, KroneckerDelta).as_explicit() == \
        Identity(2).as_explicit()

    n = symbols('n')
    assert FunctionMatrix(n, n, Lambda((i, j), 0))
    n = symbols('n', integer=False)
    raises(ValueError, lambda: FunctionMatrix(n, n, Lambda((i, j), 0)))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: FunctionMatrix(n, n, Lambda((i, j), 0)))


def test_funcmatrix():
    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
