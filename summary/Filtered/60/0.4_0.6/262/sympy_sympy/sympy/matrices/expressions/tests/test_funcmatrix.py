from sympy.core import symbols, Lambda
from sympy.functions import KroneckerDelta
from sympy.matrices import Matrix
from sympy.matrices.expressions import FunctionMatrix, MatrixExpr, Identity
from sympy.utilities.pytest import raises


def test_funcmatrix_creation():
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
    """
    Create a 3x3 FunctionMatrix with elements defined by the lambda function i - j. The matrix is indexed by symbols i and j. The resulting matrix has elements as follows:
    - X[1, 1] is 0
    - X[1, 2] is -1
    The matrix is a 3x3 square matrix, and the elements are defined by the lambda function i - j. The matrix can be used in matrix operations with other MatrixExpr objects.
    
    Parameters
    """

    i, j = symbols('i,j')
    X = FunctionMatrix(3, 3, Lambda((i, j), i - j))
    assert X[1, 1] == 0
    assert X[1, 2] == -1
    assert X.shape == (3, 3)
    assert X.rows == X.cols == 3
    assert Matrix(X) == Matrix(3, 3, lambda i, j: i - j)
    assert isinstance(X*X + X, MatrixExpr)
