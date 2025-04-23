from sympy.core.symbol import symbols
from sympy.matrices.dense import Matrix
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.tensor.array.ndim_array import NDimArray
from sympy.matrices.common import MatrixCommon
from sympy.tensor.array.array_derivatives import ArrayDerivative

x, y, z, t = symbols("x y z t")

m = Matrix([[x, y], [z, t]])

M = MatrixSymbol("M", 3, 2)
N = MatrixSymbol("N", 4, 3)


def test_array_derivative_construction():
    """
    Test the construction of the ArrayDerivative.
    
    Parameters
    ----------
    x : MatrixSymbol
    The symbol representing the variable with respect to which the derivative is taken.
    m : MatrixSymbol
    The symbol representing the matrix for which the derivative is taken.
    M : Matrix
    A matrix for testing the derivative.
    N : MatrixSymbol
    A matrix symbol for testing the derivative with multiple dimensions.
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> x = MatrixSymbol('x', 2, 2
    """


    d = ArrayDerivative(x, m, evaluate=False)
    assert d.shape == (2, 2)
    expr = d.doit()
    assert isinstance(expr, MatrixCommon)
    assert expr.shape == (2, 2)

    d = ArrayDerivative(m, m, evaluate=False)
    assert d.shape == (2, 2, 2, 2)
    expr = d.doit()
    assert isinstance(expr, NDimArray)
    assert expr.shape == (2, 2, 2, 2)

    d = ArrayDerivative(m, x, evaluate=False)
    assert d.shape == (2, 2)
    expr = d.doit()
    assert isinstance(expr, MatrixCommon)
    assert expr.shape == (2, 2)

    d = ArrayDerivative(M, N, evaluate=False)
    assert d.shape == (4, 3, 3, 2)
    expr = d.doit()
    assert isinstance(expr, ArrayDerivative)
    assert expr.shape == (4, 3, 3, 2)

    d = ArrayDerivative(M, (N, 2), evaluate=False)
    assert d.shape == (4, 3, 4, 3, 3, 2)
    expr = d.doit()
    assert isinstance(expr, ArrayDerivative)
    assert expr.shape == (4, 3, 4, 3, 3, 2)

    d = ArrayDerivative(M.as_explicit(), (N.as_explicit(), 2), evaluate=False)
    assert d.doit().shape == (4, 3, 4, 3, 3, 2)
    expr = d.doit()
    assert isinstance(expr, ArrayDerivative)
    assert expr.shape == (4, 3, 4, 3, 3, 2)
