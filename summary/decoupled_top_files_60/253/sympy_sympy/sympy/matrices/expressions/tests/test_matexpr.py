from sympy import KroneckerDelta, diff, Piecewise, And
from sympy import Sum, Dummy, factor, expand

from sympy.core import S, symbols, Add, Mul
from sympy.core.compatibility import long
from sympy.functions import transpose, sin, cos, sqrt, cbrt
from sympy.simplify import simplify
from sympy.matrices import (Identity, ImmutableMatrix, Inverse, MatAdd, MatMul,
        MatPow, Matrix, MatrixExpr, MatrixSymbol, ShapeError, ZeroMatrix,
        SparseMatrix, Transpose, Adjoint)
from sympy.matrices.expressions.matexpr import MatrixElement
from sympy.utilities.pytest import raises


n, m, l, k, p = symbols('n m l k p', integer=True)
x = symbols('x')
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)
w = MatrixSymbol('w', n, 1)


def test_shape():
    assert A.shape == (n, m)
    assert (A*B).shape == (n, l)
    raises(ShapeError, lambda: B*A)


def test_matexpr():
    assert (x*A).shape == A.shape
    assert (x*A).__class__ == MatMul
    assert 2*A - A - A == ZeroMatrix(*A.shape)
    assert (A*B).shape == (n, l)


def test_subs():
    """
    Substitute symbols in matrix expressions.
    
    Parameters:
    A, B, C (MatrixSymbol): Matrix symbols to be substituted.
    n, m, l (int): Dimensions of the matrices.
    B (MatrixSymbol): Matrix to be substituted with C.
    
    Returns:
    MatrixExpression: The resulting matrix expression after substitution.
    """

    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, l)
    C = MatrixSymbol('C', m, l)

    assert A.subs(n, m).shape == (m, m)

    assert (A*B).subs(B, C) == A*C

    assert (A*B).subs(l, n).is_square


def test_ZeroMatrix():
    A = MatrixSymbol('A', n, m)
    Z = ZeroMatrix(n, m)

    assert A + Z == A
    assert A*Z.T == ZeroMatrix(n, n)
    assert Z*A.T == ZeroMatrix(n, n)
    assert A - A == ZeroMatrix(*A.shape)

    assert not Z

    assert transpose(Z) == ZeroMatrix(m, n)
    assert Z.conjugate() == Z

    assert ZeroMatrix(n, n)**0 == Identity(n)
    with raises(ShapeError):
        Z**0
    with raises(ShapeError):
        Z**2


def test_ZeroMatrix_doit():
    """
    Test the `doit` method of the `ZeroMatrix` class.
    
    This function checks the `doit` method of the `ZeroMatrix` class, which is expected to return a zero matrix with dimensions specified by the sum of two symbolic variables `n` and `n`. The `doit` method should evaluate the sum and return a zero matrix with the correct dimensions. The resulting matrix should have its row dimension as a `Mul` object.
    
    Parameters:
    - None
    
    Returns:
    -
    """

    Znn = ZeroMatrix(Add(n, n, evaluate=False), n)
    assert isinstance(Znn.rows, Add)
    assert Znn.doit() == ZeroMatrix(2*n, n)
    assert isinstance(Znn.doit().rows, Mul)


def test_Identity():
    A = MatrixSymbol('A', n, m)
    i, j = symbols('i j')

    In = Identity(n)
    Im = Identity(m)

    assert A*Im == A
    assert In*A == A

    assert transpose(In) == In
    assert In.inverse() == In
    assert In.conjugate() == In

    assert In[i, j] != 0
    assert Sum(In[i, j], (i, 0, n-1), (j, 0, n-1)).subs(n,3).doit() == 3
    assert Sum(Sum(In[i, j], (i, 0, n-1)), (j, 0, n-1)).subs(n,3).doit() == 3


def test_Identity_doit():
    Inn = Identity(Add(n, n, evaluate=False))
    assert isinstance(Inn.rows, Add)
    assert Inn.doit() == Identity(2*n)
    assert isinstance(Inn.doit().rows, Mul)


def test_addition():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', n, m)

    assert isinstance(A + B, MatAdd)
    assert (A + B).shape == A.shape
    assert isinstance(A - A + 2*B, MatMul)

    raises(ShapeError, lambda: A + B.T)
    raises(TypeError, lambda: A + 1)
    raises(TypeError, lambda: 5 + A)
    raises(TypeError, lambda: 5 - A)

    assert A + ZeroMatrix(n, m) - A == ZeroMatrix(n, m)
    with raises(TypeError):
        ZeroMatrix(n,m) + S(0)


def test_multiplication():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, l)
    C = MatrixSymbol('C', n, n)

    assert (2*A*B).shape == (n, l)

    assert (A*0*B) == ZeroMatrix(n, l)

    raises(ShapeError, lambda: B*A)
    assert (2*A).shape == A.shape

    assert A * ZeroMatrix(m, m) * B == ZeroMatrix(n, l)

    assert C * Identity(n) * C.I == Identity(n)

    assert B/2 == S.Half*B
    raises(NotImplementedError, lambda: 2/B)

    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, n)
    assert Identity(n) * (A + B) == A + B

    assert A**2*A == A**3
    assert A**2*(A.I)**3 == A.I
    assert A**3*(A.I)**2 == A


def test_MatPow():
    """
    Test matrix power operations.
    
    Parameters
    ----------
    A : MatrixSymbol
    The base matrix.
    n : int
    The exponent.
    
    Returns
    -------
    MatPow
    The matrix power expression.
    
    Examples
    --------
    >>> from sympy import MatrixSymbol, MatPow
    >>> A = MatrixSymbol('A', n, n)
    >>> AA = MatPow(A, 2)
    >>> AA.exp
    2
    >>> AA.base
    A
    >>> (A**n).exp
    n
    >>> A**0
    """

    A = MatrixSymbol('A', n, n)

    AA = MatPow(A, 2)
    assert AA.exp == 2
    assert AA.base == A
    assert (A**n).exp == n

    assert A**0 == Identity(n)
    assert A**1 == A
    assert A**2 == AA
    assert A**-1 == Inverse(A)
    assert (A**-1)**-1 == A
    assert (A**2)**3 == A**6
    assert A**S.Half == sqrt(A)
    assert A**(S(1)/3) == cbrt(A)
    raises(ShapeError, lambda: MatrixSymbol('B', 3, 2)**2)


def test_MatrixSymbol():
    """
    Test the MatrixSymbol function.
    
    This function checks the properties of the MatrixSymbol and ensures that it correctly
    returns the shape of the matrix and raises a TypeError when attempting to evaluate
    the symbol with a specific value, as well as ensuring that the doit method does not
    alter the MatrixSymbol.
    
    Parameters:
    n (Symbol): The number of rows in the matrix.
    m (Symbol): The number of columns in the matrix.
    t (Symbol): The symbol used to test evaluation.
    
    Returns:
    None:
    """

    n, m, t = symbols('n,m,t')
    X = MatrixSymbol('X', n, m)
    assert X.shape == (n, m)
    raises(TypeError, lambda: MatrixSymbol('X', n, m)(t))  # issue 5855
    assert X.doit() == X


def test_dense_conversion():
    X = MatrixSymbol('X', 2, 2)
    assert ImmutableMatrix(X) == ImmutableMatrix(2, 2, lambda i, j: X[i, j])
    assert Matrix(X) == Matrix(2, 2, lambda i, j: X[i, j])


def test_free_symbols():
    assert (C*D).free_symbols == set((C, D))


def test_zero_matmul():
    assert isinstance(S.Zero * MatrixSymbol('X', 2, 2), MatrixExpr)


def test_matadd_simplify():
    A = MatrixSymbol('A', 1, 1)
    assert simplify(MatAdd(A, ImmutableMatrix([[sin(x)**2 + cos(x)**2]]))) == \
        MatAdd(A, ImmutableMatrix([[1]]))


def test_matmul_simplify():
    """
    Simplify the matrix multiplication of a symbolic matrix A with a matrix containing trigonometric functions.
    
    Parameters:
    A (MatrixSymbol): A symbolic matrix with dimensions 1x1.
    
    Returns:
    Matrix: The simplified matrix resulting from the multiplication of A with a matrix containing the trigonometric expression sin(x)**2 + cos(x)**2, which simplifies to 1.
    """

    A = MatrixSymbol('A', 1, 1)
    assert simplify(MatMul(A, ImmutableMatrix([[sin(x)**2 + cos(x)**2]]))) == \
        MatMul(A, ImmutableMatrix([[1]]))


def test_invariants():
    """
    Test invariants for matrix expressions.
    
    This function checks if a matrix expression is equivalent to its own class
    instantiation with the same arguments. The function iterates over a list of
    matrix objects and verifies that each object is equal to its corresponding
    class instantiated with its arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Objects:
    - Identity(n): Identity matrix of size n x n
    - ZeroMatrix(m, n): Zero matrix of size m x n
    -
    """

    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, l)
    X = MatrixSymbol('X', n, n)
    objs = [Identity(n), ZeroMatrix(m, n), A, MatMul(A, B), MatAdd(A, A),
            Transpose(A), Adjoint(A), Inverse(X), MatPow(X, 2), MatPow(X, -1),
            MatPow(X, 0)]
    for obj in objs:
        assert obj == obj.__class__(*obj.args)

def test_indexing():
    """
    Test indexing of a matrix symbol.
    
    Parameters:
    A (MatrixSymbol): A symbolic matrix of dimensions n x m.
    
    Notes:
    - Accesses individual elements using A[1, 2] for the element in the second row and third column.
    - Supports symbolic indexing with A[l, k] for general row l and column k.
    - Allows for indexing of any element in the matrix, including A[l+1, k+1] for the element in the (l+
    """

    A = MatrixSymbol('A', n, m)
    A[1, 2]
    A[l, k]
    A[l+1, k+1]


def test_single_indexing():
    A = MatrixSymbol('A', 2, 3)
    assert A[1] == A[0, 1]
    assert A[long(1)] == A[0, 1]
    assert A[3] == A[1, 0]
    assert list(A[:2, :2]) == [A[0, 0], A[0, 1], A[1, 0], A[1, 1]]
    raises(IndexError, lambda: A[6])
    raises(IndexError, lambda: A[n])
    B = MatrixSymbol('B', n, m)
    raises(IndexError, lambda: B[1])
    B = MatrixSymbol('B', n, 3)
    assert B[3] == B[1, 0]


def test_MatrixElement_commutative():
    assert A[0, 1]*A[1, 0] == A[1, 0]*A[0, 1]


def test_MatrixSymbol_determinant():
    """
    Test MatrixSymbol determinant.
    
    Parameters:
    A (MatrixSymbol): A 4x4 matrix symbol.
    
    Returns:
    The determinant of the matrix A expressed as an explicit matrix.
    """

    A = MatrixSymbol('A', 4, 4)
    assert A.as_explicit().det() == A[0, 0]*A[1, 1]*A[2, 2]*A[3, 3] - \
        A[0, 0]*A[1, 1]*A[2, 3]*A[3, 2] - A[0, 0]*A[1, 2]*A[2, 1]*A[3, 3] + \
        A[0, 0]*A[1, 2]*A[2, 3]*A[3, 1] + A[0, 0]*A[1, 3]*A[2, 1]*A[3, 2] - \
        A[0, 0]*A[1, 3]*A[2, 2]*A[3, 1] - A[0, 1]*A[1, 0]*A[2, 2]*A[3, 3] + \
        A[0, 1]*A[1, 0]*A[2, 3]*A[3, 2] + A[0, 1]*A[1, 2]*A[2, 0]*A[3, 3] - \
        A[0, 1]*A[1, 2]*A[2, 3]*A[3, 0] - A[0, 1]*A[1, 3]*A[2, 0]*A[3, 2] + \
        A[0, 1]*A[1, 3]*A[2, 2]*A[3, 0] + A[0, 2]*A[1, 0]*A[2, 1]*A[3, 3] - \
        A[0, 2]*A[1, 0]*A[2, 3]*A[3, 1] - A[0, 2]*A[1, 1]*A[2, 0]*A[3, 3] + \
        A[0, 2]*A[1, 1]*A[2, 3]*A[3, 0] + A[0, 2]*A[1, 3]*A[2, 0]*A[3, 1] - \
        A[0, 2]*A[1, 3]*A[2, 1]*A[3, 0] - A[0, 3]*A[1, 0]*A[2, 1]*A[3, 2] + \
        A[0, 3]*A[1, 0]*A[2, 2]*A[3, 1] + A[0, 3]*A[1, 1]*A[2, 0]*A[3, 2] - \
        A[0, 3]*A[1, 1]*A[2, 2]*A[3, 0] - A[0, 3]*A[1, 2]*A[2, 0]*A[3, 1] + \
        A[0, 3]*A[1, 2]*A[2, 1]*A[3, 0]


def test_MatrixElement_diff():
    assert (A[3, 0]*A[0, 0]).diff(A[0, 0]) == A[3, 0]


def test_MatrixElement_doit():
    u = MatrixSymbol('u', 2, 1)
    v = ImmutableMatrix([3, 5])
    assert u[0, 0].subs(u, v).doit() == v[0, 0]


def test_identity_powers():
    M = Identity(n)
    assert MatPow(M, 3).doit() == M**3
    assert M**n == M
    assert MatPow(M, 0).doit() == M**2
    assert M**-2 == M
    assert MatPow(M, -2).doit() == M**0
    N = Identity(3)
    assert MatPow(N, 2).doit() == N**n
    assert MatPow(N, 3).doit() == N
    assert MatPow(N, -2).doit() == N**4
    assert MatPow(N, 2).doit() == N**0


def test_Zero_power():
    """
    Test the power operation for a zero matrix.
    
    Parameters:
    - z1: A zero matrix of size n x n.
    - z2: A zero matrix of size 3 x 3.
    
    Returns:
    - None
    
    Raises:
    - ValueError: If the exponent is negative and the matrix is not square.
    
    Key operations:
    - z1**4 == z1
    - z1**0 == Identity(n)
    - MatPow(z1, 2).doit() == z1**2
    """

    z1 = ZeroMatrix(n, n)
    assert z1**4 == z1
    raises(ValueError, lambda:z1**-2)
    assert z1**0 == Identity(n)
    assert MatPow(z1, 2).doit() == z1**2
    raises(ValueError, lambda:MatPow(z1, -2).doit())
    z2 = ZeroMatrix(3, 3)
    assert MatPow(z2, 4).doit() == z2**4
    raises(ValueError, lambda:z2**-3)
    assert z2**3 == MatPow(z2, 3).doit()
    assert z2**0 == Identity(3)
    raises(ValueError, lambda:MatPow(z2, -1).doit())


def test_matrixelement_diff():
    dexpr = diff((D*w)[k,0], w[p,0])

    assert w[k, p].diff(w[k, p]) == 1
    assert w[k, p].diff(w[0, 0]) == KroneckerDelta(0, k)*KroneckerDelta(0, p)
    assert str(dexpr) == "Sum(KroneckerDelta(_i_1, p)*D[k, _i_1], (_i_1, 0, n - 1))"
    assert str(dexpr.doit()) == 'Piecewise((D[k, p], (p >= 0) & (p <= n - 1)), (0, True))'
    # TODO: bug with .dummy_eq( ), the previous 2 lines should be replaced by:
    return  # stop eval
    _i_1 = Dummy("_i_1")
    assert dexpr.dummy_eq(Sum(KroneckerDelta(_i_1, p)*D[k, _i_1], (_i_1, 0, n - 1)))
    assert dexpr.doit().dummy_eq(Piecewise((D[k, p], (p >= 0) & (p <= n - 1)), (0, True)))


def test_MatrixElement_with_values():
    x, y, z, w = symbols("x y z w")
    M = Matrix([[x, y], [z, w]])
    i, j = symbols("i, j")
    Mij = M[i, j]
    assert isinstance(Mij, MatrixElement)
    Ms = SparseMatrix([[2, 3], [4, 5]])
    msij = Ms[i, j]
    assert isinstance(msij, MatrixElement)
    for oi, oj in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        assert Mij.subs({i: oi, j: oj}) == M[oi, oj]
        assert msij.subs({i: oi, j: oj}) == Ms[oi, oj]
    A = MatrixSymbol("A", 2, 2)
    assert A[0, 0].subs(A, M) == x
    assert A[i, j].subs(A, M) == M[i, j]
    assert M[i, j].subs(M, A) == A[i, j]

    assert isinstance(M[3*i - 2, j], MatrixElement)
    assert M[3*i - 2, j].subs({i: 1, j: 0}) == M[1, 0]
    assert isinstance(M[i, 0], MatrixElement)
    assert M[i, 0].subs(i, 0) == M[0, 0]
    assert M[0, i].subs(i, 1) == M[0, 1]

    assert M[i, j].diff(x) == Matrix([[1, 0], [0, 0]])[i, j]

    raises(ValueError, lambda: M[i, 2])
    raises(ValueError, lambda: M[i, -1])
    raises(ValueError, lambda: M[2, i])
    raises(ValueError, lambda: M[-1, i])

def test_inv():
    B = MatrixSymbol('B', 3, 3)
    assert B.inv() == B**-1

def test_factor_expand():
    """
    Expand and factor matrix expressions.
    
    Parameters:
    A (MatrixSymbol): An n x n matrix symbol.
    B (MatrixSymbol): An n x n matrix symbol.
    C (MatrixSymbol): An n x n matrix symbol.
    D (MatrixSymbol): An n x n matrix symbol.
    
    This function performs two operations on matrix expressions:
    1. Expand the expression (A + B)*(C + D) to A*C + B*C + A*D + B*D.
    2. Factor the
    """

    A = MatrixSymbol("A", n, n)
    B = MatrixSymbol("B", n, n)
    expr1 = (A + B)*(C + D)
    expr2 = A*C + B*C + A*D + B*D
    assert expr1 != expr2
    assert expand(expr1) == expr2
    assert factor(expr2) == expr1
i
