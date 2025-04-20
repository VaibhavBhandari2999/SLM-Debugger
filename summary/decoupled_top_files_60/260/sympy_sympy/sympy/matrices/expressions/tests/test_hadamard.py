from sympy import Identity, OneMatrix, ZeroMatrix
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
    """
    Tests the HadamardProduct function.
    
    Parameters:
    - A: A matrix or scalar value.
    - B: A matrix or scalar value.
    - C: A matrix or scalar value.
    - n: An integer representing the number of rows in the output matrix.
    - k: An integer representing the number of columns in the output matrix.
    
    Returns:
    - A matrix resulting from the element-wise multiplication of the input matrices.
    
    Raises:
    - ShapeError: If the shapes of the input matrices do not match.
    """

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
    X = MatrixSymbol('X', 2, 2)
    Y = MatrixSymbol('Y', 2, 2)
    Z = MatrixSymbol('Z', 2, 2)

    assert (X*HadamardProduct(Y, Z))[0, 0] == \
            X[0, 0]*Y[0, 0]*Z[0, 0] + X[0, 1]*Y[1, 0]*Z[1, 0]


def test_canonicalize():
    """
    Test the canonicalization of Hadamard products.
    
    This function tests the canonicalization of Hadamard products, including the
    unpacking of certain matrices and the simplification of expressions involving
    the zero and identity matrices.
    
    Parameters:
    X, Y (MatrixSymbol): Matrix symbols used in the test expressions.
    Z (ZeroMatrix): The zero matrix used to test simplification.
    U (OneMatrix): The identity matrix used to test simplification.
    
    Returns:
    None: This function does
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


def test_hadamard_power():
    """
    Test the hadamard_power function.
    
    This function tests the hadamard_power function, which raises a matrix to a power using the Hadamard power operation. The key parameters are:
    - `A`: A matrix symbol.
    - `n`: The power to which the matrix is raised.
    
    Key points:
    - `hadamard_power(A, 1)` returns the original matrix `A`.
    - `hadamard_power(A, 2)` returns a HadamardPower object representing the
    """

    m, n, p = symbols('m, n, p', integer=True)
    A = MatrixSymbol('A', m, n)
    B = MatrixSymbol('B', m, n)
    C = MatrixSymbol('C', m, p)

    assert hadamard_power(A, 1) == A
    assert isinstance(hadamard_power(A, 2), HadamardPower)
    assert hadamard_power(A, n).T == hadamard_power(A.T, n)
    assert hadamard_power(A, n)[0, 0] == A[0, 0]**n
    assert hadamard_power(m, n) == m**n
    raises(ValueError, lambda: hadamard_power(A, A))

    # Testing printer:
    assert str(hadamard_power(A, n)) == "A.**n"
    assert str(hadamard_power(A, 1+n)) == "A.**(n + 1)"
    assert str(hadamard_power(A*B.T, 1+n)) == "(A*B.T).**(n + 1)"
