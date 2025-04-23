from sympy.utilities.pytest import raises
from sympy.core import symbols, pi, S
from sympy.matrices import Identity, MatrixSymbol, ImmutableMatrix, ZeroMatrix
from sympy.matrices.expressions import MatPow, MatAdd, MatMul
from sympy.matrices.expressions.matexpr import ShapeError

n, m, l, k = symbols('n m l k', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)


def test_entry():
    """
    Compute matrix powers.
    
    This function calculates the power of a matrix using the MatPow class from sympy.concrete.
    
    Parameters:
    A (Matrix): The matrix to be powered.
    n (int): The power to which the matrix is raised.
    
    Returns:
    Matrix: The resulting matrix after raising the input matrix to the specified power.
    
    Examples:
    >>> from sympy import Matrix
    >>> A = Matrix([[1, 2], [3, 4]])
    >>> MatPow(A
    """

    from sympy.concrete import Sum
    assert MatPow(A, 1)[0, 0] == A[0, 0]
    assert MatPow(C, 0)[0, 0] == 1
    assert MatPow(C, 0)[0, 1] == 0
    assert isinstance(MatPow(C, 2)[0, 0], Sum)


def test_as_explicit_symbol():
    X = MatrixSymbol('X', 2, 2)
    assert MatPow(X, 0).as_explicit() == ImmutableMatrix(Identity(2))
    assert MatPow(X, 1).as_explicit() == X.as_explicit()
    assert MatPow(X, 2).as_explicit() == (X.as_explicit())**2


def test_as_explicit_nonsquare_symbol():
    X = MatrixSymbol('X', 2, 3)
    assert MatPow(X, 1).as_explicit() == X.as_explicit()
    for r in [0, 2, S.Half, S.Pi]:
        raises(ShapeError, lambda: MatPow(X, r).as_explicit())


def test_as_explicit():
    A = ImmutableMatrix([[1, 2], [3, 4]])
    assert MatPow(A, 0).as_explicit() == ImmutableMatrix(Identity(2))
    assert MatPow(A, 1).as_explicit() == A
    assert MatPow(A, 2).as_explicit() == A**2
    assert MatPow(A, -1).as_explicit() == A.inv()
    assert MatPow(A, -2).as_explicit() == (A.inv())**2
    # less expensive than testing on a 2x2
    A = ImmutableMatrix([4]);
    assert MatPow(A, S.Half).as_explicit() == A**S.Half


def test_as_explicit_nonsquare():
    A = ImmutableMatrix([[1, 2, 3], [4, 5, 6]])
    assert MatPow(A, 1).as_explicit() == A
    raises(ShapeError, lambda: MatPow(A, 0).as_explicit())
    raises(ShapeError, lambda: MatPow(A, 2).as_explicit())
    raises(ShapeError, lambda: MatPow(A, -1).as_explicit())
    raises(ValueError, lambda: MatPow(A, pi).as_explicit())


def test_doit_nonsquare_MatrixSymbol():
    assert MatPow(A, 1).doit() == A
    for r in [0, 2, -1, pi]:
        assert MatPow(A, r).doit() == MatPow(A, r)


def test_doit_square_MatrixSymbol_symsize():
    assert MatPow(C, 0).doit() == Identity(n)
    assert MatPow(C, 1).doit() == C
    for r in [2, -1, pi]:
        assert MatPow(C, r).doit() == MatPow(C, r)


def test_doit_with_MatrixBase():
    """
    Test the `doit` method for the `MatPow` class with `MatrixBase` objects.
    
    This function evaluates the `doit` method for various powers of a given `MatrixBase` object `X`. It tests the identity matrix for power 0, the original matrix for power 1, the square of the matrix for power 2, and the inverse and square of the inverse for negative powers. It also tests a scalar matrix to ensure the method works for simple cases.
    
    Parameters
    """

    X = ImmutableMatrix([[1, 2], [3, 4]])
    assert MatPow(X, 0).doit() == ImmutableMatrix(Identity(2))
    assert MatPow(X, 1).doit() == X
    assert MatPow(X, 2).doit() == X**2
    assert MatPow(X, -1).doit() == X.inv()
    assert MatPow(X, -2).doit() == (X.inv())**2
    # less expensive than testing on a 2x2
    assert MatPow(ImmutableMatrix([4]), S.Half).doit() == ImmutableMatrix([2])


def test_doit_nonsquare():
    """
    Compute the matrix power of a non-square matrix.
    
    Parameters:
    X (ImmutableMatrix): A non-square matrix.
    
    Returns:
    ImmutableMatrix: The matrix power of X.
    
    Raises:
    ShapeError: If the matrix is not square or the power is not an integer.
    """

    X = ImmutableMatrix([[1, 2, 3], [4, 5, 6]])
    assert MatPow(X, 1).doit() == X
    raises(ShapeError, lambda: MatPow(X, 0).doit())
    raises(ShapeError, lambda: MatPow(X, 2).doit())
    raises(ShapeError, lambda: MatPow(X, -1).doit())
    raises(ShapeError, lambda: MatPow(X, pi).doit())


def test_doit_nested_MatrixExpr():
    X = ImmutableMatrix([[1, 2], [3, 4]])
    Y = ImmutableMatrix([[2, 3], [4, 5]])
    assert MatPow(MatMul(X, Y), 2).doit() == (X*Y)**2
    assert MatPow(MatAdd(X, Y), 2).doit() == (X + Y)**2


def test_identity_power():
    k = Identity(n)
    assert MatPow(k, 4).doit() == k
    assert MatPow(k, n).doit() == k
    assert MatPow(k, -3).doit() == k
    assert MatPow(k, 0).doit() == k
    l = Identity(3)
    assert MatPow(l, n).doit() == l
    assert MatPow(l, -1).doit() == l
    assert MatPow(l, 0).doit() == l


def test_zero_power():
    """
    Test the behavior of the MatPow function with zero matrices.
    
    Parameters:
    z1 (ZeroMatrix): A zero matrix of size n x n.
    z2 (ZeroMatrix): Another zero matrix of size 4 x 4.
    n (int): An integer representing the size of the matrices.
    
    Returns:
    None
    
    Raises:
    ValueError: If the exponent is negative and the matrix is not the zero matrix.
    
    Actions:
    - Assert that raising a zero matrix of size n x n to the power of
    """

    z1 = ZeroMatrix(n, n)
    assert MatPow(z1, 3).doit() == z1
    raises(ValueError, lambda:MatPow(z1, -1).doit())
    assert MatPow(z1, 0).doit() == Identity(n)
    assert MatPow(z1, n).doit() == z1
    raises(ValueError, lambda:MatPow(z1, -2).doit())
    z2 = ZeroMatrix(4, 4)
    assert MatPow(z2, n).doit() == z2
    raises(ValueError, lambda:MatPow(z2, -3).doit())
    assert MatPow(z2, 2).doit() == z2
    assert MatPow(z2, 0).doit() == Identity(4)
    raises(ValueError, lambda:MatPow(z2, -1).doit())
(ValueError, lambda:MatPow(z2, -1).doit())

