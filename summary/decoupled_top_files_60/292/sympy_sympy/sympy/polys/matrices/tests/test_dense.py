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
    """
    Add two 2D lists element-wise.
    
    This function adds two 2D lists (a and b) element-wise and updates the first list (a) in place.
    
    Parameters:
    a (list of list of int/float): The first 2D list to be updated.
    b (list of list of int/float): The second 2D list to be added to the first list.
    
    Returns:
    None: The function modifies the first list (a)
    """

    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    ddm_iadd(a, b)
    assert a == [[6, 8], [10, 12]]


def test_ddm_isub():
    """
    Subtract one DDM from another in-place.
    
    This function subtracts the elements of the second DDM (b) from the first DDM (a) and updates the first DDM in-place.
    
    Parameters:
    a (list of list of int/float): The first DDM, which will be updated in-place.
    b (list of list of int/float): The second DDM, which will be subtracted from the first DDM.
    
    Returns:
    None: The function
    """

    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    ddm_isub(a, b)
    assert a == [[-4, -4], [-4, -4]]


def test_ddm_ineg():
    a = [[1, 2], [3, 4]]
    ddm_ineg(a)
    assert a == [[-1, -2], [-3, -4]]


def test_ddm_matmul():
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
    """
    Calculate the determinant of a diagonal dominance matrix (DDM) using the identity element.
    
    This function computes the determinant of a given diagonal dominance matrix (DDM) using the identity element of the specified ring.
    
    Parameters:
    A (list of lists): The diagonal dominance matrix represented as a list of lists.
    R (ring): The ring in which the determinant is computed.
    
    Returns:
    element of R: The determinant of the matrix A as an element of the specified ring.
    """

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
    """
    Split a lower triangular matrix L and an upper triangular matrix U into their ILU factors.
    
    This function performs an incomplete LU factorization (ILU) on the given lower triangular matrix L and upper triangular matrix U. The ILU factorization is a decomposition of a matrix into the product of a lower triangular matrix and an upper triangular matrix, with some modifications to improve numerical stability.
    
    Parameters:
    L (list of list of Rational): The lower triangular matrix.
    U (list of list of Rational
    """

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
    """
    Compute the characteristic polynomial of a dense matrix using Berkowitz's algorithm.
    
    Parameters:
    - A (list of lists or DDM): The dense matrix for which the characteristic polynomial is to be computed.
    - R (Ring): The ring in which the coefficients of the characteristic polynomial are to be computed.
    
    Returns:
    - list: The coefficients of the characteristic polynomial of the matrix A.
    
    Raises:
    - DMShapeError: If the input matrix is not square.
    
    Examples:
    - For an empty matrix, the characteristic
    """

    A = []
    assert ddm_berk(A, ZZ) == [[ZZ(1)]]

    A = [[ZZ(1), ZZ(2), ZZ(3)], [ZZ(4), ZZ(5), ZZ(6)], [ZZ(7), ZZ(8), ZZ(9)]]
    Avec = [[ZZ(1)], [ZZ(-15)], [ZZ(-18)], [ZZ(0)]]
    assert ddm_berk(A, ZZ) == Avec

    A = DDM([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    raises(DMShapeError, lambda: ddm_berk(A, ZZ))
ises(DMShapeError, lambda: ddm_berk(A, ZZ))
