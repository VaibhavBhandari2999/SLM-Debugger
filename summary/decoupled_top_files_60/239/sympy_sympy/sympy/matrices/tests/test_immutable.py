from itertools import product

from sympy import (ImmutableMatrix, Matrix, eye, zeros, S, Equality,
        Unequality, ImmutableSparseMatrix, SparseMatrix, sympify,
        integrate)
from sympy.abc import x, y
from sympy.utilities.pytest import raises

IM = ImmutableMatrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
ieye = ImmutableMatrix(eye(3))


def test_immutable_creation():
    """
    Function to test the creation of an immutable matrix.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function asserts that the shape of the matrix 'IM' is (3, 3).
    - It also checks that the element at position (1, 2) is 6 and the element at position (2, 2) is 9.
    """

    assert IM.shape == (3, 3)
    assert IM[1, 2] == 6
    assert IM[2, 2] == 9


def test_immutability():
    with raises(TypeError):
        IM[2, 2] = 5


def test_slicing():
    assert IM[1, :] == ImmutableMatrix([[4, 5, 6]])
    assert IM[:2, :2] == ImmutableMatrix([[1, 2], [4, 5]])


def test_subs():
    A = ImmutableMatrix([[1, 2], [3, 4]])
    B = ImmutableMatrix([[1, 2], [x, 4]])
    C = ImmutableMatrix([[-x, x*y], [-(x + y), y**2]])
    assert B.subs(x, 3) == A
    assert (x*B).subs(x, 3) == 3*A
    assert (x*eye(2) + B).subs(x, 3) == 3*eye(2) + A
    assert C.subs([[x, -1], [y, -2]]) == A
    assert C.subs([(x, -1), (y, -2)]) == A
    assert C.subs({x: -1, y: -2}) == A
    assert C.subs({x: y - 1, y: x - 1}, simultaneous=True) == \
        ImmutableMatrix([[1 - y, (x - 1)*(y - 1)], [2 - x - y, (x - 1)**2]])


def test_as_immutable():
    """
    Convert a Matrix to an ImmutableMatrix.
    
    This function takes a Matrix and converts it into an ImmutableMatrix, which is an immutable version of the Matrix. The ImmutableMatrix cannot be modified after creation, ensuring data integrity.
    
    Parameters:
    X (Matrix): The Matrix to be converted to an ImmutableMatrix.
    
    Returns:
    ImmutableMatrix: An immutable version of the input Matrix.
    If the input is already an ImmutableMatrix, it is returned unchanged.
    If the input is a SparseMatrix, it is
    """

    X = Matrix([[1, 2], [3, 4]])
    assert sympify(X) == X.as_immutable() == ImmutableMatrix([[1, 2], [3, 4]])
    X = SparseMatrix(5, 5, {})
    assert sympify(X) == X.as_immutable() == ImmutableSparseMatrix(
            [[0 for i in range(5)] for i in range(5)])


def test_function_return_types():
    # Lets ensure that decompositions of immutable matrices remain immutable
    # I.e. do MatrixBase methods return the correct class?
    X = ImmutableMatrix([[1, 2], [3, 4]])
    Y = ImmutableMatrix([[1], [0]])
    q, r = X.QRdecomposition()
    assert (type(q), type(r)) == (ImmutableMatrix, ImmutableMatrix)

    assert type(X.LUsolve(Y)) == ImmutableMatrix
    assert type(X.QRsolve(Y)) == ImmutableMatrix

    X = ImmutableMatrix([[1, 2], [2, 1]])
    assert X.T == X
    assert X.is_symmetric
    assert type(X.cholesky()) == ImmutableMatrix
    L, D = X.LDLdecomposition()
    assert (type(L), type(D)) == (ImmutableMatrix, ImmutableMatrix)

    assert X.is_diagonalizable()
    assert X.det() == -3
    assert X.norm(2) == 3

    assert type(X.eigenvects()[0][2][0]) == ImmutableMatrix

    assert type(zeros(3, 3).as_immutable().nullspace()[0]) == ImmutableMatrix

    X = ImmutableMatrix([[1, 0], [2, 1]])
    assert type(X.lower_triangular_solve(Y)) == ImmutableMatrix
    assert type(X.T.upper_triangular_solve(Y)) == ImmutableMatrix

    assert type(X.minor_submatrix(0, 0)) == ImmutableMatrix

# issue 6279
# https://github.com/sympy/sympy/issues/6279
# Test that Immutable _op_ Immutable => Immutable and not MatExpr


def test_immutable_evaluation():
    X = ImmutableMatrix(eye(3))
    A = ImmutableMatrix(3, 3, range(9))
    assert isinstance(X + A, ImmutableMatrix)
    assert isinstance(X * A, ImmutableMatrix)
    assert isinstance(X * 2, ImmutableMatrix)
    assert isinstance(2 * X, ImmutableMatrix)
    assert isinstance(A**2, ImmutableMatrix)


def test_deterimant():
    assert ImmutableMatrix(4, 4, lambda i, j: i + j).det() == 0


def test_Equality():
    assert Equality(IM, IM) is S.true
    assert Unequality(IM, IM) is S.false
    assert Equality(IM, IM.subs(1, 2)) is S.false
    assert Unequality(IM, IM.subs(1, 2)) is S.true
    assert Equality(IM, 2) is S.false
    assert Unequality(IM, 2) is S.true
    M = ImmutableMatrix([x, y])
    assert Equality(M, IM) is S.false
    assert Unequality(M, IM) is S.true
    assert Equality(M, M.subs(x, 2)).subs(x, 2) is S.true
    assert Unequality(M, M.subs(x, 2)).subs(x, 2) is S.false
    assert Equality(M, M.subs(x, 2)).subs(x, 3) is S.false
    assert Unequality(M, M.subs(x, 2)).subs(x, 3) is S.true


def test_integrate():
    """
    Test the integration of a 2D array (IM) with respect to the variable x.
    
    This function integrates a given 2D array `IM` over the variable `x` and checks if the resulting integrated array `intIM` has the same shape as the input array. It also verifies that each element in the integrated array is equal to the corresponding element in the input array multiplied by the linear function (1 + j + 3*i)*x, where i and j are the indices
    """

    intIM = integrate(IM, x)
    assert intIM.shape == IM.shape
    assert all([intIM[i, j] == (1 + j + 3*i)*x for i, j in
                product(range(3), range(3))])
