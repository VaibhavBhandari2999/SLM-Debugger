from sympy.core.singleton import S
from sympy.core.symbol import symbols
from sympy.matrices import Matrix
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.matrices.expressions.sets import MatrixSet
from sympy.matrices.expressions.special import ZeroMatrix
from sympy.testing.pytest import raises


def test_MatrixSet():
    """
    Create a MatrixSet object.
    
    This function creates a MatrixSet object with specified shape and set.
    
    Parameters:
    n (int): Number of rows in the matrix.
    m (int): Number of columns in the matrix.
    set (Set): The set of elements that the matrix can contain.
    
    Returns:
    MatrixSet: A MatrixSet object with the specified shape and set.
    
    Examples:
    >>> M = MatrixSet(2, 2, set=S.Reals)
    >>> M.shape
    """

    n, m = symbols('n m', integer=True)
    A = MatrixSymbol('A', n, m)
    C = MatrixSymbol('C', n, n)

    M = MatrixSet(2, 2, set=S.Reals)
    assert M.shape == (2, 2)
    assert M.set == S.Reals
    X = Matrix([[1, 2], [3, 4]])
    assert X in M
    X = ZeroMatrix(2, 2)
    assert X in M
    raises(TypeError, lambda: A in M)
    raises(TypeError, lambda: 1 in M)
    M = MatrixSet(n, m, set=S.Reals)
    assert A in M
    raises(TypeError, lambda: C in M)
    raises(TypeError, lambda: X in M)
    M = MatrixSet(2, 2, set={1, 2, 3})
    X = Matrix([[1, 2], [3, 4]])
    Y = Matrix([[1, 2]])
    assert (X in M) == S.false
    assert (Y in M) == S.false
    raises(ValueError, lambda: MatrixSet(2, -2, S.Reals))
    raises(ValueError, lambda: MatrixSet(2.4, -1, S.Reals))
    raises(TypeError, lambda: MatrixSet(2, 2, (1, 2, 3)))
