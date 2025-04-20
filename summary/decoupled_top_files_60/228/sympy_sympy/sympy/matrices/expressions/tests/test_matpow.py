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
    Compute matrix powers and evaluate specific entries.
    
    This function evaluates specific entries of matrix powers and checks the correctness of the results.
    
    Parameters:
    A (Matrix): The base matrix for the power operation.
    C (Matrix): Another base matrix for the power operation.
    
    Returns:
    None: This function does not return any value. It prints the results of the evaluations.
    
    Examples:
    >>> A = Matrix([[1, 2], [3, 4]])
    >>> C = Matrix([[0,
    """

    from sympy.concrete import Sum
    assert MatPow(A, 1)[0, 0] == A[0, 0]
    assert MatPow(C, 0)[0, 0] == 1
    assert MatPow(C, 0)[0, 1] == 0
    assert isinstance(MatPow(C, 2)[0, 0], Sum)


def test_as_explicit_symbol():
    """
    Generate the explicit form of a matrix power.
    
    This function takes a MatrixSymbol and an integer exponent, and returns the
    matrix power as an explicit matrix. For an exponent of 0, it returns the
    identity matrix of the same size. For an exponent of 1, it returns the original
    matrix. For higher exponents, it squares the matrix repeatedly.
    
    Parameters:
    X (MatrixSymbol): The matrix symbol for which the power is to be computed.
    exp (int): The
    """

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
    """
    Perform the matrix power operation on a MatrixSymbol.
    
    This function computes the matrix power of a given MatrixSymbol. It supports
    raising a MatrixSymbol to a scalar power. The function can handle various
    scalar values including integers, floats, and symbolic constants.
    
    Parameters:
    A (MatrixSymbol): The matrix symbol to be raised to a power.
    
    Returns:
    MatrixSymbol: The result of raising the input MatrixSymbol to the given power.
    
    Examples:
    >>> A = MatrixSymbol('A',
    """

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
    Test the `doit` method for MatrixBase objects.
    
    This function tests the `doit` method for various MatrixBase operations, including matrix exponentiation, inversion, and scalar exponentiation.
    
    Parameters:
    - X (MatrixBase): The input matrix for the operations.
    
    Returns:
    - The result of the `doit` method for the specified operations on the input matrix.
    
    Key Operations Tested:
    - Matrix exponentiation (positive and negative powers).
    - Matrix inversion.
    - Scalar exponentiation.
    
    Examples:
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
    """
    Test the identity matrix power functionality.
    
    Parameters:
    n (int): The exponent to which the identity matrix is raised.
    
    This function tests the MatPow operation on an identity matrix. It checks the results for positive, negative, and zero exponents, ensuring that the identity matrix is returned for any exponent.
    """

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
    raises(ValueError, lambda:MatPow(z2, -1).doit())
