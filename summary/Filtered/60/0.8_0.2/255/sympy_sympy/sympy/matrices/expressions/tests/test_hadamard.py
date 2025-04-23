from sympy.core import symbols
from sympy.utilities.pytest import raises

from sympy.matrices import ShapeError, MatrixSymbol
from sympy.matrices.expressions import HadamardProduct, hadamard_product

n, m, k = symbols('n,m,k')
Z = MatrixSymbol('Z', n, n)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', n, m)
C = MatrixSymbol('C', m, k)

def test_HadamardProduct():
    """
    Test the HadamardProduct function.
    
    Parameters:
    - A (Matrix): First input matrix.
    - B (Matrix): Second input matrix.
    - n (Matrix): Third input matrix.
    
    Returns:
    - Matrix: Result of the Hadamard product operation.
    
    Raises:
    - ShapeError: If the shapes of the input matrices do not match.
    - TypeError: If the inputs are not matrices or are of incorrect type.
    
    Examples:
    - HadamardProduct(A, B, A) should return a matrix
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
    """
    Test mixed indexing for HadamardProduct.
    
    Parameters
    ----------
    X, Y, Z : MatrixSymbols
    2x2 matrices used in the HadamardProduct and matrix multiplication.
    
    Returns
    -------
    Expression
    The result of the expression (X*HadamardProduct(Y, Z))[0, 0], which is a symbolic expression representing the element at the first row and first column of the resulting matrix.
    """

    X = MatrixSymbol('X', 2, 2)
    Y = MatrixSymbol('Y', 2, 2)
    Z = MatrixSymbol('Z', 2, 2)

    assert (X*HadamardProduct(Y, Z))[0, 0] == \
            X[0, 0]*Y[0, 0]*Z[0, 0] + X[0, 1]*Y[1, 0]*Z[1, 0]

def test_canonicalize():
    X = MatrixSymbol('X', 2, 2)
    expr = HadamardProduct(X, check=False)
    assert isinstance(expr, HadamardProduct)
    expr2 = expr.doit() # unpack is called
    assert isinstance(expr2, MatrixSymbol)

def test_hadamard():
    m, n, p = symbols('m, n, p', integer=True)
    A = MatrixSymbol('A', m, n)
    B = MatrixSymbol('B', m, n)
    C = MatrixSymbol('C', m, p)
    with raises(TypeError):
        hadamard_product()
    assert hadamard_product(A) == A
    assert isinstance(hadamard_product(A, B), HadamardProduct)
    assert hadamard_product(A, B).doit() == hadamard_product(A, B)
    with raises(ShapeError):
        hadamard_product(A, C)
