from sympy import Matrix, symbols, MatrixSymbol, NDimArray
from sympy.matrices.common import MatrixCommon
from sympy.tensor.array.array_derivatives import ArrayDerivative

x, y, z, t = symbols("x y z t")

m = Matrix([[x, y], [z, t]])

M = MatrixSymbol("M", 3, 2)
N = MatrixSymbol("N", 4, 3)


def test_array_derivative_construction():
    """
    Test the construction of the `ArrayDerivative` object for various input cases.
    
    Parameters
    ----------
    x : MatrixSymbol
    The symbol representing the variable with respect to which the derivative is taken.
    m : MatrixSymbol
    The matrix symbol for which the derivative is taken.
    M : Matrix
    A matrix for which the derivative is taken.
    N : MatrixSymbol
    Another matrix symbol for which the derivative is taken.
    
    Returns
    -------
    None
    
    Notes
    -----
    This function tests the construction of the
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
