from sympy import Identity, OneMatrix, ZeroMatrix, Matrix, MatAdd
from sympy.core import symbols
from sympy.utilities.pytest import raises

from sympy.matrices import ShapeError, MatrixSymbol
from sympy.matrices.expressions import (HadamardProduct, hadamard_product, HadamardPower, hadamard_power)

n, m, k = symbols('n,m,k')
Z = MatrixSymbol('Z', n, n)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', n, m)
C = MatrixSymbol('C', m, k)


def test_HadamardProduct():
    assert HadamardProduct(A, B, A).shape == A.shape

    raises(ShapeError, lambda: HadamardProduct(A, B.T))
    raises(TypeError,  lambda: HadamardProduct(A, n))
    raises(TypeError,  lambda: HadamardProduct(A, 1))

    assert HadamardProduct(A, 2*B, -A)[1, 1] == \
            -2 * A[1, 1] * B[1, 1] * A[1, 1]

    mix = HadamardProduct(Z*A, B)*C
    assert mix.shape == (n, k)

    assert set(HadamardProduct(A, B, A).T.args) == set((A.T, A.T, B.T))


def test_HadamardProduct_isnt_commutative():
    assert HadamardProduct(A, B) != HadamardProduct(B, A)


def test_mixed_indexing():
    """
    Test mixed indexing for HadamardProduct.
    
    Parameters
    ----------
    X, Y, Z : MatrixSymbol
    2x2 matrices used in the HadamardProduct and matrix multiplication.
    
    Returns
    -------
    Expression
    The result of the HadamardProduct of Y and Z, followed by matrix multiplication with X, and the value at the (0, 0) index of the result.
    """

    X = MatrixSymbol('X', 2, 2)
    Y = MatrixSymbol('Y', 2, 2)
    Z = MatrixSymbol('Z', 2, 2)

    assert (X*HadamardProduct(Y, Z))[0, 0] == \
            X[0, 0]*Y[0, 0]*Z[0, 0] + X[0, 1]*Y[1, 0]*Z[1, 0]


def test_canonicalize():
    """
    Test the canonicalization of Hadamard products.
    
    Parameters:
    X (MatrixSymbol): A 2x2 matrix symbol.
    Y (MatrixSymbol): Another 2x2 matrix symbol.
    expr (HadamardProduct): The Hadamard product expression to be tested.
    
    Returns:
    None: This function does not return anything. It tests the canonicalization of Hadamard products and prints the results.
    """

    X = MatrixSymbol('X', 2, 2)
    Y = MatrixSymbol('Y', 2, 2)
    expr = HadamardProduct(X, check=False)
    assert isinstance(expr, HadamardProduct)
    expr2 = expr.doit() # unpack is called
    assert isinstance(expr2, MatrixSymbol)
    Z = ZeroMatrix(2, 2)
    U = OneMatrix(2, 2)
    assert HadamardProduct(Z, X).doit() == Z
    assert HadamardProduct(U, X, X, U).doit() == HadamardPower(X, 2)
    assert HadamardProduct(X, U, Y).doit() == HadamardProduct(X, Y)
    assert HadamardProduct(X, Z, U, Y).doit() == Z



def test_hadamard():
    m, n, p = symbols('m, n, p', integer=True)
    A = MatrixSymbol('A', m, n)
    B = MatrixSymbol('B', m, n)
    C = MatrixSymbol('C', m, p)
    X = MatrixSymbol('X', m, m)
    I = Identity(m)
    with raises(TypeError):
        hadamard_product()
    assert hadamard_product(A) == A
    assert isinstance(hadamard_product(A, B), HadamardProduct)
    assert hadamard_product(A, B).doit() == hadamard_product(A, B)
    with raises(ShapeError):
        hadamard_product(A, C)
        hadamard_product(A, I)
    assert hadamard_product(X, I) == X
    assert isinstance(hadamard_product(X, I), MatrixSymbol)

    a = MatrixSymbol("a", k, 1)
    expr = MatAdd(ZeroMatrix(k, 1), OneMatrix(k, 1))
    expr = HadamardProduct(expr, a)
    assert expr.doit() == a


def test_hadamard_product_with_explicit_mat():
    A = MatrixSymbol("A", 3, 3).as_explicit()
    B = MatrixSymbol("B", 3, 3).as_explicit()
    X = MatrixSymbol("X", 3, 3)
    expr = hadamard_product(A, B)
    ret = Matrix([i*j for i, j in zip(A, B)]).reshape(3, 3)
    assert expr == ret
    expr = hadamard_product(A, X, B)
    assert expr == HadamardProduct(ret, X)


def test_hadamard_power():
    """
    Test the Hadamard power of a matrix.
    
    Parameters:
    m, n, p (Symbol): Integer symbols representing matrix dimensions or exponents.
    A (MatrixSymbol): Symbol representing a matrix.
    
    Returns:
    HadamardPower: The Hadamard power of the matrix A raised to the power n.
    MatrixSymbol: The result of raising an integer m to the power n.
    
    Examples:
    >>> m, n, p = symbols('m, n, p', integer=True)
    >>> A = Matrix
    """

    m, n, p = symbols('m, n, p', integer=True)
    A = MatrixSymbol('A', m, n)

    assert hadamard_power(A, 1) == A
    assert isinstance(hadamard_power(A, 2), HadamardPower)
    assert hadamard_power(A, n).T == hadamard_power(A.T, n)
    assert hadamard_power(A, n)[0, 0] == A[0, 0]**n
    assert hadamard_power(m, n) == m**n
    raises(ValueError, lambda: hadamard_power(A, A))


def test_hadamard_power_explicit():
    from sympy.matrices import Matrix
    A = MatrixSymbol('A', 2, 2)
    B = MatrixSymbol('B', 2, 2)
    a, b = symbols('a b')

    assert HadamardPower(a, b) == a**b

    assert HadamardPower(a, B).as_explicit() == \
        Matrix([
            [a**B[0, 0], a**B[0, 1]],
            [a**B[1, 0], a**B[1, 1]]])

    assert HadamardPower(A, b).as_explicit() == \
        Matrix([
            [A[0, 0]**b, A[0, 1]**b],
            [A[1, 0]**b, A[1, 1]**b]])

    assert HadamardPower(A, B).as_explicit() == \
        Matrix([
            [A[0, 0]**B[0, 0], A[0, 1]**B[0, 1]],
            [A[1, 0]**B[1, 0], A[1, 1]**B[1, 1]]])
