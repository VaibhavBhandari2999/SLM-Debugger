from sympy.core.add import Add
from sympy.core.expr import unchanged
from sympy.core.mul import Mul
from sympy.core.symbol import symbols
from sympy.core.relational import Eq
from sympy.concrete.summations import Sum
from sympy.functions.elementary.piecewise import Piecewise
from sympy.matrices.common import NonSquareMatrixError, ShapeError
from sympy.matrices.immutable import ImmutableDenseMatrix
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.matrices.expressions.matadd import MatAdd
from sympy.matrices.expressions.special import (
    ZeroMatrix, GenericZeroMatrix, Identity, GenericIdentity, OneMatrix)
from sympy.matrices.expressions.matmul import MatMul
from sympy.testing.pytest import raises


def test_zero_matrix_creation():
    assert unchanged(ZeroMatrix, 2, 2)
    assert unchanged(ZeroMatrix, 0, 0)
    raises(ValueError, lambda: ZeroMatrix(-1, 2))
    raises(ValueError, lambda: ZeroMatrix(2.0, 2))
    raises(ValueError, lambda: ZeroMatrix(2j, 2))
    raises(ValueError, lambda: ZeroMatrix(2, -1))
    raises(ValueError, lambda: ZeroMatrix(2, 2.0))
    raises(ValueError, lambda: ZeroMatrix(2, 2j))

    n = symbols('n')
    assert unchanged(ZeroMatrix, n, n)
    n = symbols('n', integer=False)
    raises(ValueError, lambda: ZeroMatrix(n, n))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: ZeroMatrix(n, n))


def test_generic_zero_matrix():
    """
    Test function for the GenericZeroMatrix.
    
    This function checks the behavior of the GenericZeroMatrix class and its interactions with other matrix symbols.
    
    Parameters:
    - z: The GenericZeroMatrix instance.
    - A: A MatrixSymbol instance with shape (n, n).
    
    Returns:
    - None
    
    Key Points:
    - The function verifies that the GenericZeroMatrix instance is equal to itself and not equal to a MatrixSymbol instance.
    - It confirms that the GenericZeroMatrix instance is an instance of ZeroMatrix.
    -
    """

    z = GenericZeroMatrix()
    n = symbols('n', integer=True)
    A = MatrixSymbol("A", n, n)

    assert z == z
    assert z != A
    assert A != z

    assert z.is_ZeroMatrix

    raises(TypeError, lambda: z.shape)
    raises(TypeError, lambda: z.rows)
    raises(TypeError, lambda: z.cols)

    assert MatAdd() == z
    assert MatAdd(z, A) == MatAdd(A)
    # Make sure it is hashable
    hash(z)


def test_identity_matrix_creation():
    """
    Test the creation of identity matrices.
    
    This function checks the creation of identity matrices with different sizes and types of inputs. It verifies that identity matrices are created successfully for valid integer sizes, and raises appropriate errors for invalid inputs such as negative integers, non-integers, and non-integer symbols.
    
    Key Parameters:
    - `n`: An integer representing the size of the identity matrix to be created.
    
    Keywords:
    - None
    
    Returns:
    - None
    
    Raises:
    - ValueError: If the input is a negative integer
    """

    assert Identity(2)
    assert Identity(0)
    raises(ValueError, lambda: Identity(-1))
    raises(ValueError, lambda: Identity(2.0))
    raises(ValueError, lambda: Identity(2j))

    n = symbols('n')
    assert Identity(n)
    n = symbols('n', integer=False)
    raises(ValueError, lambda: Identity(n))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: Identity(n))


def test_generic_identity():
    I = GenericIdentity()
    n = symbols('n', integer=True)
    A = MatrixSymbol("A", n, n)

    assert I == I
    assert I != A
    assert A != I

    assert I.is_Identity
    assert I**-1 == I

    raises(TypeError, lambda: I.shape)
    raises(TypeError, lambda: I.rows)
    raises(TypeError, lambda: I.cols)

    assert MatMul() == I
    assert MatMul(I, A) == MatMul(A)
    # Make sure it is hashable
    hash(I)


def test_one_matrix_creation():
    """
    Test the creation of a OneMatrix.
    
    - `2, 2`: Creates a 2x2 OneMatrix.
    - `0, 0`: Creates a 0x0 OneMatrix.
    - `1, 1`: Creates a 1x1 OneMatrix which is equivalent to an Identity matrix.
    - `-1, 2`: Raises ValueError.
    - `2.0, 2`: Raises ValueError.
    - `2j, 2`: Raises ValueError.
    - `2,
    """

    assert OneMatrix(2, 2)
    assert OneMatrix(0, 0)
    assert Eq(OneMatrix(1, 1), Identity(1))
    raises(ValueError, lambda: OneMatrix(-1, 2))
    raises(ValueError, lambda: OneMatrix(2.0, 2))
    raises(ValueError, lambda: OneMatrix(2j, 2))
    raises(ValueError, lambda: OneMatrix(2, -1))
    raises(ValueError, lambda: OneMatrix(2, 2.0))
    raises(ValueError, lambda: OneMatrix(2, 2j))

    n = symbols('n')
    assert OneMatrix(n, n)
    n = symbols('n', integer=False)
    raises(ValueError, lambda: OneMatrix(n, n))
    n = symbols('n', negative=True)
    raises(ValueError, lambda: OneMatrix(n, n))



def test_ZeroMatrix():
    n, m = symbols('n m', integer=True)
    A = MatrixSymbol('A', n, m)
    Z = ZeroMatrix(n, m)

    assert A + Z == A
    assert A*Z.T == ZeroMatrix(n, n)
    assert Z*A.T == ZeroMatrix(n, n)
    assert A - A == ZeroMatrix(*A.shape)

    assert Z

    assert Z.transpose() == ZeroMatrix(m, n)
    assert Z.conjugate() == Z

    assert ZeroMatrix(n, n)**0 == Identity(n)
    with raises(NonSquareMatrixError):
        Z**0
    with raises(NonSquareMatrixError):
        Z**1
    with raises(NonSquareMatrixError):
        Z**2

    assert ZeroMatrix(3, 3).as_explicit() == ImmutableDenseMatrix.zeros(3, 3)


def test_ZeroMatrix_doit():
    n = symbols('n', integer=True)
    Znn = ZeroMatrix(Add(n, n, evaluate=False), n)
    assert isinstance(Znn.rows, Add)
    assert Znn.doit() == ZeroMatrix(2*n, n)
    assert isinstance(Znn.doit().rows, Mul)


def test_OneMatrix():
    """
    Test the properties and operations of the OneMatrix class.
    
    This function tests the OneMatrix class, which represents a matrix with all elements equal to 1. It checks the shape, addition, transpose, conjugate, power, and explicit representation of the matrix.
    
    Parameters:
    - n (Symbol): The number of rows in the matrix.
    - m (Symbol): The number of columns in the matrix.
    
    Returns:
    - None: This function does not return any value. It prints the results of the tests
    """

    n, m = symbols('n m', integer=True)
    A = MatrixSymbol('A', n, m)
    a = MatrixSymbol('a', n, 1)
    U = OneMatrix(n, m)

    assert U.shape == (n, m)
    assert isinstance(A + U, Add)
    assert U.transpose() == OneMatrix(m, n)
    assert U.conjugate() == U

    assert OneMatrix(n, n) ** 0 == Identity(n)
    with raises(NonSquareMatrixError):
        U ** 0
    with raises(NonSquareMatrixError):
        U ** 1
    with raises(NonSquareMatrixError):
        U ** 2
    with raises(ShapeError):
        a + U

    U = OneMatrix(n, n)
    assert U[1, 2] == 1

    U = OneMatrix(2, 3)
    assert U.as_explicit() == ImmutableDenseMatrix.ones(2, 3)


def test_OneMatrix_doit():
    """
    Test the `doit` method of the `OneMatrix` class.
    
    This function checks the behavior of the `doit` method for the `OneMatrix` class when the matrix's rows are defined as an addition of symbols. The `doit` method should evaluate the expression in the rows attribute if possible.
    
    Parameters:
    - n (Symbol): An integer symbol representing the dimension of the matrix.
    
    Returns:
    - OneMatrix: The evaluated `OneMatrix` with the rows attribute as a multiplication
    """

    n = symbols('n', integer=True)
    Unn = OneMatrix(Add(n, n, evaluate=False), n)
    assert isinstance(Unn.rows, Add)
    assert Unn.doit() == OneMatrix(2 * n, n)
    assert isinstance(Unn.doit().rows, Mul)


def test_OneMatrix_mul():
    n, m, k = symbols('n m k', integer=True)
    w = MatrixSymbol('w', n, 1)
    assert OneMatrix(n, m) * OneMatrix(m, k) == OneMatrix(n, k) * m
    assert w * OneMatrix(1, 1) == w
    assert OneMatrix(1, 1) * w.T == w.T


def test_Identity():
    n, m = symbols('n m', integer=True)
    A = MatrixSymbol('A', n, m)
    i, j = symbols('i j')

    In = Identity(n)
    Im = Identity(m)

    assert A*Im == A
    assert In*A == A

    assert In.transpose() == In
    assert In.inverse() == In
    assert In.conjugate() == In

    assert In[i, j] != 0
    assert Sum(In[i, j], (i, 0, n-1), (j, 0, n-1)).subs(n,3).doit() == 3
    assert Sum(Sum(In[i, j], (i, 0, n-1)), (j, 0, n-1)).subs(n,3).doit() == 3

    # If range exceeds the limit `(0, n-1)`, do not remove `Piecewise`:
    expr = Sum(In[i, j], (i, 0, n-1))
    assert expr.doit() == 1
    expr = Sum(In[i, j], (i, 0, n-2))
    assert expr.doit().dummy_eq(
        Piecewise(
            (1, (j >= 0) & (j <= n-2)),
            (0, True)
        )
    )
    expr = Sum(In[i, j], (i, 1, n-1))
    assert expr.doit().dummy_eq(
        Piecewise(
            (1, (j >= 1) & (j <= n-1)),
            (0, True)
        )
    )
    assert Identity(3).as_explicit() == ImmutableDenseMatrix.eye(3)


def test_Identity_doit():
    """
    Test the Identity matrix's doit method.
    
    This function checks the behavior of the `doit` method on an Identity matrix
    with a symbolic argument. It verifies that the rows attribute remains an Add
    object after applying `doit`, and that the result of `doit` is an Identity
    matrix with a Mul object as its rows.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses the `sympy` library's `symbols` and `Identity` functions
    """

    n = symbols('n', integer=True)
    Inn = Identity(Add(n, n, evaluate=False))
    assert isinstance(Inn.rows, Add)
    assert Inn.doit() == Identity(2*n)
    assert isinstance(Inn.doit().rows, Mul)
