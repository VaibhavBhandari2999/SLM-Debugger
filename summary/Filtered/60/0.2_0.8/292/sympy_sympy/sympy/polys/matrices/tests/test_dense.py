from sympy.testing.pytest import raises

from sympy.polys import ZZ, QQ

from sympy.polys.matrices.ddm import DDM
from sympy.polys.matrices.dense import (
        ddm_transpose,
        ddm_iadd, ddm_isub, ddm_ineg, ddm_imatmul, ddm_imul, ddm_irref,
        ddm_idet, ddm_iinv, ddm_ilu, ddm_ilu_split, ddm_ilu_solve, ddm_berk)
from sympy.polys.matrices.exceptions import (
    DMShapeError, DMNonInvertibleMatrixError, DMNonSquareMatrixError)


def test_ddm_transpose():
    a = [[1, 2], [3, 4]]
    assert ddm_transpose(a) == [[1, 3], [2, 4]]


def test_ddm_iadd():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    ddm_iadd(a, b)
    assert a == [[6, 8], [10, 12]]


def test_ddm_isub():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    ddm_isub(a, b)
    assert a == [[-4, -4], [-4, -4]]


def test_ddm_ineg():
    a = [[1, 2], [3, 4]]
    ddm_ineg(a)
    assert a == [[-1, -2], [-3, -4]]


def test_ddm_matmul():
    """
    Multiply a matrix by a scalar in-place.
    
    Parameters:
    a (list of list of int/float): The matrix to be multiplied.
    scalar (int/float): The scalar value to multiply the matrix by.
    
    Returns:
    None: The function modifies the matrix in-place and does not return anything.
    """

    a = [[1, 2], [3, 4]]
    ddm_imul(a, 2)
    assert a == [[2, 4], [6, 8]]

    a = [[1, 2], [3, 4]]
    ddm_imul(a, 0)
    assert a == [[0, 0], [0, 0]]


def test_ddm_imatmul():
    a = [[1, 2, 3], [4, 5, 6]]
    b = [[1, 2], [3, 4], [5, 6]]

    c1 = [[0, 0], [0, 0]]
    ddm_imatmul(c1, a, b)
    assert c1 == [[22, 28], [49, 64]]

    c2 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    ddm_imatmul(c2, b, a)
    assert c2 == [[9, 12, 15], [19, 26, 33], [29, 40, 51]]

    b3 = [[1], [2], [3]]
    c3 = [[0], [0]]
    ddm_imatmul(c3, a, b3)
    assert c3 == [[14], [32]]


def test_ddm_irref():
    """
    Perform Inverse Row Reduction (IRREF) on a matrix.
    
    This function takes a matrix `A` and performs inverse row reduction to
    transform it into its row-reduced echelon form (IRREF). The function
    returns a list of pivot indices and modifies the matrix in place.
    
    Parameters:
    A (list of list of Rational): The input matrix to be transformed.
    
    Returns:
    list: A list of pivot indices indicating the columns that contain
    the pivots in the row-re
    """

    # Empty matrix
    A = []
    Ar = []
    pivots = []
    assert ddm_irref(A) == pivots
    assert A == Ar

    # Standard square case
    A = [[QQ(0), QQ(1)], [QQ(1), QQ(1)]]
    Ar = [[QQ(1), QQ(0)], [QQ(0), QQ(1)]]
    pivots = [0, 1]
    assert ddm_irref(A) == pivots
    assert A == Ar

    # m < n  case
    A = [[QQ(1), QQ(2), QQ(1)], [QQ(3), QQ(4), QQ(1)]]
    Ar = [[QQ(1), QQ(0), QQ(-1)], [QQ(0), QQ(1), QQ(1)]]
    pivots = [0, 1]
    assert ddm_irref(A) == pivots
    assert A == Ar

    # same m < n  but reversed
    A = [[QQ(3), QQ(4), QQ(1)], [QQ(1), QQ(2), QQ(1)]]
    Ar = [[QQ(1), QQ(0), QQ(-1)], [QQ(0), QQ(1), QQ(1)]]
    pivots = [0, 1]
    assert ddm_irref(A) == pivots
    assert A == Ar

    # m > n case
    A = [[QQ(1), QQ(0)], [QQ(1), QQ(3)], [QQ(0), QQ(1)]]
    Ar = [[QQ(1), QQ(0)], [QQ(0), QQ(1)], [QQ(0), QQ(0)]]
    pivots = [0, 1]
    assert ddm_irref(A) == pivots
    assert A == Ar

    # Example with missing pivot
    A = [[QQ(1), QQ(0), QQ(1)], [QQ(3), QQ(0), QQ(1)]]
    Ar = [[QQ(1), QQ(0), QQ(0)], [QQ(0), QQ(0), QQ(1)]]
    pivots = [0, 2]
    assert ddm_irref(A) == pivots
    assert A == Ar

    # Example with missing pivot and no replacement
    A = [[QQ(0), QQ(1)], [QQ(0), QQ(2)], [QQ(1), QQ(0)]]
    Ar = [[QQ(1), QQ(0)], [QQ(0), QQ(1)], [QQ(0), QQ(0)]]
    pivots = [0, 1]
    assert ddm_irref(A) == pivots
    assert A == Ar


def test_ddm_idet():
    A = []
    assert ddm_idet(A, ZZ) == ZZ(1)

    A = [[ZZ(2)]]
    assert ddm_idet(A, ZZ) == ZZ(2)

    A = [[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]]
    assert ddm_idet(A, ZZ) == ZZ(-2)

    A = [[ZZ(1), ZZ(2), ZZ(3)], [ZZ(1), ZZ(2), ZZ(4)], [ZZ(1), ZZ(3), ZZ(5)]]
    assert ddm_idet(A, ZZ) == ZZ(-1)

    A = [[ZZ(1), ZZ(2), ZZ(3)], [ZZ(1), ZZ(2), ZZ(4)], [ZZ(1), ZZ(2), ZZ(5)]]
    assert ddm_idet(A, ZZ) == ZZ(0)

    A = [[QQ(1, 2), QQ(1, 2)], [QQ(1, 3), QQ(1, 4)]]
    assert ddm_idet(A, QQ) == QQ(-1, 24)


def test_ddm_inv():
    """
    Invert a dense matrix over a given field.
    
    Parameters:
    Ainv (list): The matrix to be inverted.
    A (list): The original matrix.
    QQ (object): The field over which the matrix is defined.
    
    Returns:
    None: The function modifies Ainv in place to store the inverse of A.
    
    Raises:
    ValueError: If the field is not appropriate for the matrix.
    DMNonSquareMatrixError: If the matrix is not square.
    DMNonInvert
    """

    A = []
    Ainv = []
    ddm_iinv(Ainv, A, QQ)
    assert Ainv == A

    A = []
    Ainv = []
    raises(ValueError, lambda: ddm_iinv(Ainv, A, ZZ))

    A = [[QQ(1), QQ(2)]]
    Ainv = [[QQ(0), QQ(0)]]
    raises(DMNonSquareMatrixError, lambda: ddm_iinv(Ainv, A, QQ))

    A = [[QQ(1, 1), QQ(2, 1)], [QQ(3, 1), QQ(4, 1)]]
    Ainv = [[QQ(0), QQ(0)], [QQ(0), QQ(0)]]
    Ainv_expected = [[QQ(-2, 1), QQ(1, 1)], [QQ(3, 2), QQ(-1, 2)]]
    ddm_iinv(Ainv, A, QQ)
    assert Ainv == Ainv_expected

    A = [[QQ(1, 1), QQ(2, 1)], [QQ(2, 1), QQ(4, 1)]]
    Ainv = [[QQ(0), QQ(0)], [QQ(0), QQ(0)]]
    raises(DMNonInvertibleMatrixError, lambda: ddm_iinv(Ainv, A, QQ))


def test_ddm_ilu():
    A = []
    Alu = []
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []

    A = [[]]
    Alu = [[]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []

    A = [[QQ(1), QQ(2)], [QQ(3), QQ(4)]]
    Alu = [[QQ(1), QQ(2)], [QQ(3), QQ(-2)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []

    A = [[QQ(0), QQ(2)], [QQ(3), QQ(4)]]
    Alu = [[QQ(3), QQ(4)], [QQ(0), QQ(2)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == [(0, 1)]

    A = [[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(5), QQ(6)], [QQ(7), QQ(8), QQ(9)]]
    Alu = [[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(-3), QQ(-6)], [QQ(7), QQ(2), QQ(0)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []

    A = [[QQ(0), QQ(1), QQ(2)], [QQ(0), QQ(1), QQ(3)], [QQ(1), QQ(1), QQ(2)]]
    Alu = [[QQ(1), QQ(1), QQ(2)], [QQ(0), QQ(1), QQ(3)], [QQ(0), QQ(1), QQ(-1)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == [(0, 2)]

    A = [[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(5), QQ(6)]]
    Alu = [[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(-3), QQ(-6)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []

    A = [[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]]
    Alu = [[QQ(1), QQ(2)], [QQ(3), QQ(-2)], [QQ(5), QQ(2)]]
    swaps = ddm_ilu(A)
    assert A == Alu
    assert swaps == []


def test_ddm_ilu_split():
    U = []
    L = []
    Uexp = []
    Lexp = []
    swaps = ddm_ilu_split(L, U, QQ)
    assert U == Uexp
    assert L == Lexp
    assert swaps == []

    U = [[]]
    L = [[QQ(1)]]
    Uexp = [[]]
    Lexp = [[QQ(1)]]
    swaps = ddm_ilu_split(L, U, QQ)
    assert U == Uexp
    assert L == Lexp
    assert swaps == []

    U = [[QQ(1), QQ(2)], [QQ(3), QQ(4)]]
    L = [[QQ(1), QQ(0)], [QQ(0), QQ(1)]]
    Uexp = [[QQ(1), QQ(2)], [QQ(0), QQ(-2)]]
    Lexp = [[QQ(1), QQ(0)], [QQ(3), QQ(1)]]
    swaps = ddm_ilu_split(L, U, QQ)
    assert U == Uexp
    assert L == Lexp
    assert swaps == []

    U = [[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(5), QQ(6)]]
    L = [[QQ(1), QQ(0)], [QQ(0), QQ(1)]]
    Uexp = [[QQ(1), QQ(2), QQ(3)], [QQ(0), QQ(-3), QQ(-6)]]
    Lexp = [[QQ(1), QQ(0)], [QQ(4), QQ(1)]]
    swaps = ddm_ilu_split(L, U, QQ)
    assert U == Uexp
    assert L == Lexp
    assert swaps == []

    U = [[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]]
    L = [[QQ(1), QQ(0), QQ(0)], [QQ(0), QQ(1), QQ(0)], [QQ(0), QQ(0), QQ(1)]]
    Uexp = [[QQ(1), QQ(2)], [QQ(0), QQ(-2)], [QQ(0), QQ(0)]]
    Lexp = [[QQ(1), QQ(0), QQ(0)], [QQ(3), QQ(1), QQ(0)], [QQ(5), QQ(2), QQ(1)]]
    swaps = ddm_ilu_split(L, U, QQ)
    assert U == Uexp
    assert L == Lexp
    assert swaps == []


def test_ddm_ilu_solve():
    """
    Solve a linear system using the Incomplete LU (ILU) factorization.
    
    This function solves the linear system `A * x = b` using the Incomplete LU
    factorization of the matrix `A`. The factorization is given by `A = L * U`, where
    `L` is a lower triangular matrix and `U` is an upper triangular matrix. The
    function also handles row swaps to ensure the system is solved correctly.
    
    Parameters:
    x (DDM):
    """

    # Basic example
    # A = [[QQ(1), QQ(2)], [QQ(3), QQ(4)]]
    U = [[QQ(1), QQ(2)], [QQ(0), QQ(-2)]]
    L = [[QQ(1), QQ(0)], [QQ(3), QQ(1)]]
    swaps = []
    b = DDM([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    x = DDM([[QQ(0)], [QQ(0)]], (2, 1), QQ)
    xexp = DDM([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    ddm_ilu_solve(x, L, U, swaps, b)
    assert x == xexp

    # Example with swaps
    # A = [[QQ(0), QQ(2)], [QQ(3), QQ(4)]]
    U = [[QQ(3), QQ(4)], [QQ(0), QQ(2)]]
    L = [[QQ(1), QQ(0)], [QQ(0), QQ(1)]]
    swaps = [(0, 1)]
    b = DDM([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    x = DDM([[QQ(0)], [QQ(0)]], (2, 1), QQ)
    xexp = DDM([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    ddm_ilu_solve(x, L, U, swaps, b)
    assert x == xexp

    # Overdetermined, consistent
    # A = DDM([[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]], (3, 2), QQ)
    U = [[QQ(1), QQ(2)], [QQ(0), QQ(-2)], [QQ(0), QQ(0)]]
    L = [[QQ(1), QQ(0), QQ(0)], [QQ(3), QQ(1), QQ(0)], [QQ(5), QQ(2), QQ(1)]]
    swaps = []
    b = DDM([[QQ(1)], [QQ(2)], [QQ(3)]], (3, 1), QQ)
    x = DDM([[QQ(0)], [QQ(0)]], (2, 1), QQ)
    xexp = DDM([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    ddm_ilu_solve(x, L, U, swaps, b)
    assert x == xexp

    # Overdetermined, inconsistent
    b = DDM([[QQ(1)], [QQ(2)], [QQ(4)]], (3, 1), QQ)
    raises(DMNonInvertibleMatrixError, lambda: ddm_ilu_solve(x, L, U, swaps, b))

    # Square, noninvertible
    # A = DDM([[QQ(1), QQ(2)], [QQ(1), QQ(2)]], (2, 2), QQ)
    U = [[QQ(1), QQ(2)], [QQ(0), QQ(0)]]
    L = [[QQ(1), QQ(0)], [QQ(1), QQ(1)]]
    swaps = []
    b = DDM([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    raises(DMNonInvertibleMatrixError, lambda: ddm_ilu_solve(x, L, U, swaps, b))

    # Underdetermined
    # A = DDM([[QQ(1), QQ(2)]], (1, 2), QQ)
    U = [[QQ(1), QQ(2)]]
    L = [[QQ(1)]]
    swaps = []
    b = DDM([[QQ(3)]], (1, 1), QQ)
    raises(NotImplementedError, lambda: ddm_ilu_solve(x, L, U, swaps, b))

    # Shape mismatch
    b3 = DDM([[QQ(1)], [QQ(2)], [QQ(3)]], (3, 1), QQ)
    raises(DMShapeError, lambda: ddm_ilu_solve(x, L, U, swaps, b3))

    # Empty shape mismatch
    U = [[QQ(1)]]
    L = [[QQ(1)]]
    swaps = []
    x = [[QQ(1)]]
    b = []
    raises(DMShapeError, lambda: ddm_ilu_solve(x, L, U, swaps, b))

    # Empty system
    U = []
    L = []
    swaps = []
    b = []
    x = []
    ddm_ilu_solve(x, L, U, swaps, b)
    assert x == []


def test_ddm_charpoly():
    A = []
    assert ddm_berk(A, ZZ) == [[ZZ(1)]]

    A = [[ZZ(1), ZZ(2), ZZ(3)], [ZZ(4), ZZ(5), ZZ(6)], [ZZ(7), ZZ(8), ZZ(9)]]
    Avec = [[ZZ(1)], [ZZ(-15)], [ZZ(-18)], [ZZ(0)]]
    assert ddm_berk(A, ZZ) == Avec

    A = DDM([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    raises(DMShapeError, lambda: ddm_berk(A, ZZ))
