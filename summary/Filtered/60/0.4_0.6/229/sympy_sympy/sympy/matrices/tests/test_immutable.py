from itertools import product

from sympy import (ImmutableMatrix, Matrix, eye, zeros, S, Equality,
        Unequality, ImmutableSparseMatrix, SparseMatrix, sympify,
        integrate)
from sympy.abc import x, y
from sympy.utilities.pytest import raises

IM = ImmutableMatrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
ieye = ImmutableMatrix(eye(3))


def test_immutable_creation():
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
    """
    Substitute values in an immutable matrix.
    
    This function substitutes specified values in an immutable matrix. It supports substituting a single variable, multiple variables, or a dictionary of substitutions. The function can handle expressions and simultaneous substitutions.
    
    Parameters:
    A (ImmutableMatrix): The input immutable matrix.
    B (ImmutableMatrix): Another input immutable matrix for comparison or substitution.
    C (ImmutableMatrix): A third immutable matrix for simultaneous substitution.
    x, y (Symbol): Symbols to be substituted in the matrices
    """

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
    X = Matrix([[1, 2], [3, 4]])
    assert sympify(X) == X.as_immutable() == ImmutableMatrix([[1, 2], [3, 4]])
    X = SparseMatrix(5, 5, {})
    assert sympify(X) == X.as_immutable() == ImmutableSparseMatrix(
            [[0 for i in range(5)] for i in range(5)])


def test_function_return_types():
    """
    Tests the return types of various methods in the ImmutableMatrix class.
    
    This function ensures that decompositions of immutable matrices remain immutable and checks that the methods return the correct class. It also tests other methods such as solving linear systems, checking symmetry, performing Cholesky decomposition, LDL decomposition, diagonalizability, computing the determinant, calculating the norm, finding eigenvectors, and solving triangular systems.
    
    Key methods tested:
    - QRdecomposition: Returns the Q and R matrices as ImmutableMatrices.
    -
    """

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
    assert X.berkowitz_det() == -3
    assert X.norm(2) == 3

    assert type(X.eigenvects()[0][2][0]) == ImmutableMatrix

    assert type(zeros(3, 3).as_immutable().nullspace()[0]) == ImmutableMatrix

    X = ImmutableMatrix([[1, 0], [2, 1]])
    assert type(X.lower_triangular_solve(Y)) == ImmutableMatrix
    assert type(X.T.upper_triangular_solve(Y)) == ImmutableMatrix

    assert type(X.minorMatrix(0, 0)) == ImmutableMatrix

# issue 6279
# https://github.com/sympy/sympy/issues/6279
# Test that Immutable _op_ Immutable => Immutable and not MatExpr


def test_immutable_evaluation():
    """
    Test the evaluation of arithmetic operations on ImmutableMatrix objects.
    
    This function checks the behavior of various arithmetic operations involving ImmutableMatrix objects. It ensures that the operations return the correct types and that the operations are performed as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    X (ImmutableMatrix): An identity matrix of size 3x3.
    A (ImmutableMatrix): A 3x3 matrix with elements ranging from 0 to 8.
    
    Operations tested:
    - Addition:
    """

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
    intIM = integrate(IM, x)
    assert intIM.shape == IM.shape
    assert all([intIM[i, j] == (1 + j + 3*i)*x for i, j in
                product(range(3), range(3))])
