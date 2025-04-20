from sympy.testing.pytest import raises

from sympy.core.numbers import Rational
from sympy.functions import sqrt

from sympy.matrices.common import (NonInvertibleMatrixError,
    NonSquareMatrixError, ShapeError)
from sympy.matrices.dense import Matrix
from sympy.polys import ZZ, QQ


from sympy.polys.matrices.domainmatrix import DomainMatrix, DomainScalar
from sympy.polys.matrices.exceptions import (DDMBadInputError, DDMDomainError,
        DDMShapeError, DDMFormatError)
from sympy.polys.matrices.ddm import DDM
from sympy.polys.matrices.sdm import SDM


def test_DomainMatrix_init():
    lol = [[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]]
    dod = {0: {0: ZZ(1), 1:ZZ(2)}, 1: {0:ZZ(3), 1:ZZ(4)}}
    ddm = DDM(lol, (2, 2), ZZ)
    sdm = SDM(dod, (2, 2), ZZ)

    A = DomainMatrix(lol, (2, 2), ZZ)
    assert A.rep == ddm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    A = DomainMatrix(dod, (2, 2), ZZ)
    assert A.rep == sdm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    raises(TypeError, lambda: DomainMatrix(ddm, (2, 2), ZZ))
    raises(TypeError, lambda: DomainMatrix(sdm, (2, 2), ZZ))
    raises(TypeError, lambda: DomainMatrix(Matrix([[1]]), (1, 1), ZZ))

    for fmt, rep in [('sparse', sdm), ('dense', ddm)]:
        A = DomainMatrix(lol, (2, 2), ZZ, fmt=fmt)
        assert A.rep == rep
        A = DomainMatrix(dod, (2, 2), ZZ, fmt=fmt)
        assert A.rep == rep

    raises(ValueError, lambda: DomainMatrix(lol, (2, 2), ZZ, fmt='invalid'))

    raises(DDMBadInputError, lambda: DomainMatrix([[ZZ(1), ZZ(2)]], (2, 2), ZZ))


def test_DomainMatrix_from_rep():
    ddm = DDM([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A = DomainMatrix.from_rep(ddm)
    assert A.rep == ddm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    sdm = SDM({0: {0: ZZ(1), 1:ZZ(2)}, 1: {0:ZZ(3), 1:ZZ(4)}}, (2, 2), ZZ)
    A = DomainMatrix.from_rep(sdm)
    assert A.rep == sdm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    A = DomainMatrix([[ZZ(1)]], (1, 1), ZZ)
    raises(TypeError, lambda: DomainMatrix.from_rep(A))


def test_DomainMatrix_from_list_sympy():
    """
    Create a DomainMatrix from a list of lists using SymPy.
    
    This function constructs a DomainMatrix from a given list of lists, where the elements are converted to the specified domain. It supports both basic and algebraic number fields.
    
    Parameters:
    rows (int): Number of rows in the matrix.
    cols (int): Number of columns in the matrix.
    list_of_lists (List[List[Union[int, float, sympy.Basic]]]): A list of lists containing the elements of the matrix
    """

    ddm = DDM([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A = DomainMatrix.from_list_sympy(2, 2, [[1, 2], [3, 4]])
    assert A.rep == ddm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    K = QQ.algebraic_field(sqrt(2))
    ddm = DDM(
        [[K.convert(1 + sqrt(2)), K.convert(2 + sqrt(2))],
         [K.convert(3 + sqrt(2)), K.convert(4 + sqrt(2))]],
        (2, 2),
        K
    )
    A = DomainMatrix.from_list_sympy(
        2, 2, [[1 + sqrt(2), 2 + sqrt(2)], [3 + sqrt(2), 4 + sqrt(2)]],
        extension=True)
    assert A.rep == ddm
    assert A.shape == (2, 2)
    assert A.domain == K


def test_DomainMatrix_from_dict_sympy():
    sdm = SDM({0: {0: QQ(1, 2)}, 1: {1: QQ(2, 3)}}, (2, 2), QQ)
    sympy_dict = {0: {0: Rational(1, 2)}, 1: {1: Rational(2, 3)}}
    A = DomainMatrix.from_dict_sympy(2, 2, sympy_dict)
    assert A.rep == sdm
    assert A.shape == (2, 2)
    assert A.domain == QQ

    fds = DomainMatrix.from_dict_sympy
    raises(DDMBadInputError, lambda: fds(2, 2, {3: {0: Rational(1, 2)}}))
    raises(DDMBadInputError, lambda: fds(2, 2, {0: {3: Rational(1, 2)}}))


def test_DomainMatrix_from_Matrix():
    sdm = SDM({0: {0: ZZ(1), 1: ZZ(2)}, 1: {0: ZZ(3), 1: ZZ(4)}}, (2, 2), ZZ)
    A = DomainMatrix.from_Matrix(Matrix([[1, 2], [3, 4]]))
    assert A.rep == sdm
    assert A.shape == (2, 2)
    assert A.domain == ZZ

    K = QQ.algebraic_field(sqrt(2))
    sdm = SDM(
        {0: {0: K.convert(1 + sqrt(2)), 1: K.convert(2 + sqrt(2))},
         1: {0: K.convert(3 + sqrt(2)), 1: K.convert(4 + sqrt(2))}},
        (2, 2),
        K
    )
    A = DomainMatrix.from_Matrix(
        Matrix([[1 + sqrt(2), 2 + sqrt(2)], [3 + sqrt(2), 4 + sqrt(2)]]),
        extension=True)
    assert A.rep == sdm
    assert A.shape == (2, 2)
    assert A.domain == K

    A = DomainMatrix.from_Matrix(Matrix([[QQ(1, 2), QQ(3, 4)], [QQ(0, 1), QQ(0, 1)]]), fmt='dense')
    ddm = DDM([[QQ(1, 2), QQ(3, 4)], [QQ(0, 1), QQ(0, 1)]], (2, 2), QQ)

    assert A.rep == ddm
    assert A.shape == (2, 2)
    assert A.domain == QQ


def test_DomainMatrix_eq():
    """
    Test if two DomainMatrix objects are equal.
    
    Parameters:
    A (DomainMatrix): The first DomainMatrix object to compare.
    B (DomainMatrix): The second DomainMatrix object to compare.
    
    Returns:
    bool: True if the two DomainMatrix objects are equal, False otherwise.
    
    Note:
    - The comparison is based on the equality of the elements and the shape of the DomainMatrix objects.
    - A DomainMatrix object and a list of lists with the same elements and shape are considered unequal.
    """

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A == A
    B = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(1)]], (2, 2), ZZ)
    assert A != B
    C = [[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]]
    assert A != C


def test_DomainMatrix_get_domain():
    K, items = DomainMatrix.get_domain([1, 2, 3, 4])
    assert items == [ZZ(1), ZZ(2), ZZ(3), ZZ(4)]
    assert K == ZZ

    K, items = DomainMatrix.get_domain([1, 2, 3, Rational(1, 2)])
    assert items == [QQ(1), QQ(2), QQ(3), QQ(1, 2)]
    assert K == QQ


def test_DomainMatrix_convert_to():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = A.convert_to(QQ)
    assert Aq == DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)


def test_DomainMatrix_to_field():
    """
    Convert a DomainMatrix to a field matrix.
    
    This function takes a DomainMatrix and converts it to a matrix over a field.
    
    Parameters:
    A (DomainMatrix): The input DomainMatrix to be converted.
    
    Returns:
    DomainMatrix: A new DomainMatrix over the field, equivalent to the input.
    
    Example:
    >>> A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    >>> Aq =
    """

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = A.to_field()
    assert Aq == DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)


def test_DomainMatrix_to_sparse():
    """
    Convert a DomainMatrix to its sparse representation.
    
    Parameters:
    - A (DomainMatrix): The DomainMatrix object to be converted.
    
    Returns:
    - A_sparse (SparseMatrix): The sparse representation of the input DomainMatrix.
    """

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A_sparse = A.to_sparse()
    assert A_sparse.rep == {0: {0: 1, 1: 2}, 1: {0: 3, 1: 4}}


def test_DomainMatrix_to_dense():
    A = DomainMatrix({0: {0: 1, 1: 2}, 1: {0: 3, 1: 4}}, (2, 2), ZZ)
    A_dense = A.to_dense()
    assert A_dense.rep == DDM([[1, 2], [3, 4]], (2, 2), ZZ)


def test_DomainMatrix_unify():
    """
    Unify the domains of two DomainMatrix objects.
    
    This function takes two DomainMatrix objects and unifies their domains to a common domain. If the domains are already the same, the original matrices are returned. The function supports unification to either dense or sparse format.
    
    Parameters:
    Az (DomainMatrix): The first DomainMatrix object.
    Aq (DomainMatrix): The second DomainMatrix object.
    fmt (str, optional): The format of the resulting matrices ('dense' or 'sparse').
    """

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    assert Az.unify(Az) == (Az, Az)
    assert Az.unify(Aq) == (Aq, Aq)
    assert Aq.unify(Az) == (Aq, Aq)
    assert Aq.unify(Aq) == (Aq, Aq)

    As = DomainMatrix({0: {1: ZZ(1)}, 1:{0:ZZ(2)}}, (2, 2), ZZ)
    Ad = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)

    assert As.unify(As) == (As, As)
    assert Ad.unify(Ad) == (Ad, Ad)

    Bs, Bd = As.unify(Ad, fmt='dense')
    assert Bs.rep == DDM([[0, 1], [2, 0]], (2, 2), ZZ)
    assert Bd.rep == DDM([[1, 2],[3, 4]], (2, 2), ZZ)

    Bs, Bd = As.unify(Ad, fmt='sparse')
    assert Bs.rep == SDM({0: {1: 1}, 1: {0: 2}}, (2, 2), ZZ)
    assert Bd.rep == SDM({0: {0: 1, 1: 2}, 1: {0: 3, 1: 4}}, (2, 2), ZZ)

    raises(ValueError, lambda: As.unify(Ad, fmt='invalid'))


def test_DomainMatrix_to_Matrix():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A.to_Matrix() == Matrix([[1, 2], [3, 4]])


def test_DomainMatrix_repr():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert repr(A) == 'DomainMatrix([[1, 2], [3, 4]], (2, 2), ZZ)'


def test_DomainMatrix_transpose():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    AT = DomainMatrix([[ZZ(1), ZZ(3)], [ZZ(2), ZZ(4)]], (2, 2), ZZ)
    assert A.transpose() == AT


def test_DomainMatrix_flat():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A.flat() == [ZZ(1), ZZ(2), ZZ(3), ZZ(4)]


def test_DomainMatrix_is_zero_matrix():
    """
    Test if a DomainMatrix is a zero matrix.
    
    Parameters
    ----------
    A : DomainMatrix
    The matrix to be tested.
    
    Returns
    -------
    bool
    True if the matrix is a zero matrix, False otherwise.
    """

    A = DomainMatrix([[ZZ(1)]], (1, 1), ZZ)
    B = DomainMatrix([[ZZ(0)]], (1, 1), ZZ)
    assert A.is_zero_matrix is False
    assert B.is_zero_matrix is True


def test_DomainMatrix_add():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    B = DomainMatrix([[ZZ(2), ZZ(4)], [ZZ(6), ZZ(8)]], (2, 2), ZZ)
    assert A + A == A.add(A) == B

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    L = [[2, 3], [3, 4]]
    raises(TypeError, lambda: A + L)
    raises(TypeError, lambda: L + A)

    A1 = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A2 = DomainMatrix([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    raises(DDMShapeError, lambda: A1 + A2)
    raises(DDMShapeError, lambda: A2 + A1)
    raises(DDMShapeError, lambda: A1.add(A2))
    raises(DDMShapeError, lambda: A2.add(A1))

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Asum = DomainMatrix([[QQ(2), QQ(4)], [QQ(6), QQ(8)]], (2, 2), QQ)
    assert Az + Aq == Asum
    assert Aq + Az == Asum
    raises(DDMDomainError, lambda: Az.add(Aq))
    raises(DDMDomainError, lambda: Aq.add(Az))

    As = DomainMatrix({0: {1: ZZ(1)}, 1: {0: ZZ(2)}}, (2, 2), ZZ)
    Ad = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)

    Asd = As + Ad
    Ads = Ad + As
    assert Asd == DomainMatrix([[1, 3], [5, 4]], (2, 2), ZZ)
    assert Asd.rep == DDM([[1, 3], [5, 4]], (2, 2), ZZ)
    assert Ads == DomainMatrix([[1, 3], [5, 4]], (2, 2), ZZ)
    assert Ads.rep == DDM([[1, 3], [5, 4]], (2, 2), ZZ)
    raises(DDMFormatError, lambda: As.add(Ad))


def test_DomainMatrix_sub():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    B = DomainMatrix([[ZZ(0), ZZ(0)], [ZZ(0), ZZ(0)]], (2, 2), ZZ)
    assert A - A == A.sub(A) == B

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    L = [[2, 3], [3, 4]]
    raises(TypeError, lambda: A - L)
    raises(TypeError, lambda: L - A)

    A1 = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A2 = DomainMatrix([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    raises(DDMShapeError, lambda: A1 - A2)
    raises(DDMShapeError, lambda: A2 - A1)
    raises(DDMShapeError, lambda: A1.sub(A2))
    raises(DDMShapeError, lambda: A2.sub(A1))

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Adiff = DomainMatrix([[QQ(0), QQ(0)], [QQ(0), QQ(0)]], (2, 2), QQ)
    assert Az - Aq == Adiff
    assert Aq - Az == Adiff
    raises(DDMDomainError, lambda: Az.sub(Aq))
    raises(DDMDomainError, lambda: Aq.sub(Az))

    As = DomainMatrix({0: {1: ZZ(1)}, 1: {0: ZZ(2)}}, (2, 2), ZZ)
    Ad = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)

    Asd = As - Ad
    Ads = Ad - As
    assert Asd == DomainMatrix([[-1, -1], [-1, -4]], (2, 2), ZZ)
    assert Asd.rep == DDM([[-1, -1], [-1, -4]], (2, 2), ZZ)
    assert Asd == -Ads
    assert Asd.rep == -Ads.rep


def test_DomainMatrix_neg():
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aneg = DomainMatrix([[ZZ(-1), ZZ(-2)], [ZZ(-3), ZZ(-4)]], (2, 2), ZZ)
    assert -A == A.neg() == Aneg


def test_DomainMatrix_mul():
    """
    Test the multiplication of DomainMatrix objects.
    
    Parameters
    ----------
    A : DomainMatrix
    The first matrix to be multiplied.
    A2 : DomainMatrix
    The second matrix to be multiplied, used to verify the result.
    L : list
    A list to test the TypeError raised during multiplication.
    
    Returns
    -------
    DomainMatrix
    The result of the multiplication of A and A2.
    
    Raises
    ------
    TypeError
    If the multiplication is attempted with incompatible types.
    DDMDomainError
    If the
    """

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A2 = DomainMatrix([[ZZ(7), ZZ(10)], [ZZ(15), ZZ(22)]], (2, 2), ZZ)
    assert A*A == A.matmul(A) == A2

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    L = [[1, 2], [3, 4]]
    raises(TypeError, lambda: A * L)
    raises(TypeError, lambda: L * A)

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    Aq = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Aprod = DomainMatrix([[QQ(7), QQ(10)], [QQ(15), QQ(22)]], (2, 2), QQ)
    assert Az * Aq == Aprod
    assert Aq * Az == Aprod
    raises(DDMDomainError, lambda: Az.matmul(Aq))
    raises(DDMDomainError, lambda: Aq.matmul(Az))

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    AA = DomainMatrix([[ZZ(2), ZZ(4)], [ZZ(6), ZZ(8)]], (2, 2), ZZ)
    x = ZZ(2)
    assert A * x == x * A == A.mul(x) == AA

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    AA = DomainMatrix([[ZZ(0), ZZ(0)], [ZZ(0), ZZ(0)]], (2, 2), ZZ)
    x = ZZ(0)
    assert A * x == x * A == A.mul(x) == AA

    As = DomainMatrix({0: {1: ZZ(1)}, 1: {0: ZZ(2)}}, (2, 2), ZZ)
    Ad = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)

    Asd = As * Ad
    Ads = Ad * As
    assert Asd == DomainMatrix([[3, 4], [2, 4]], (2, 2), ZZ)
    assert Asd.rep == DDM([[3, 4], [2, 4]], (2, 2), ZZ)
    assert Ads == DomainMatrix([[4, 1], [8, 3]], (2, 2), ZZ)
    assert Ads.rep == DDM([[4, 1], [8, 3]], (2, 2), ZZ)


def test_DomainMatrix_pow():
    eye = DomainMatrix.eye(2, ZZ)
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    A2 = DomainMatrix([[ZZ(7), ZZ(10)], [ZZ(15), ZZ(22)]], (2, 2), ZZ)
    A3 = DomainMatrix([[ZZ(37), ZZ(54)], [ZZ(81), ZZ(118)]], (2, 2), ZZ)
    assert A**0 == A.pow(0) == eye
    assert A**1 == A.pow(1) == A
    assert A**2 == A.pow(2) == A2
    assert A**3 == A.pow(3) == A3

    raises(TypeError, lambda: A ** Rational(1, 2))
    raises(NotImplementedError, lambda: A ** -1)
    raises(NotImplementedError, lambda: A.pow(-1))

    A = DomainMatrix.zeros((2, 1), ZZ)
    raises(NonSquareMatrixError, lambda: A ** 1)


def test_DomainMatrix_rref():
    """
    Compute the reduced row echelon form (RREF) of a DomainMatrix.
    
    This function returns a tuple containing the reduced row echelon form of the
    input matrix and a tuple of pivot indices.
    
    Parameters:
    A (DomainMatrix): The input matrix to be transformed into RREF.
    
    Returns:
    Ar (DomainMatrix): The reduced row echelon form of the input matrix.
    pivots (tuple): A tuple of pivot indices.
    
    Examples:
    >>> from diofant.polys.domains
    """

    A = DomainMatrix([], (0, 1), QQ)
    assert A.rref() == (A, ())

    A = DomainMatrix([[QQ(1)]], (1, 1), QQ)
    assert A.rref() == (A, (0,))

    A = DomainMatrix([[QQ(0)]], (1, 1), QQ)
    assert A.rref() == (A, ())

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Ar, pivots = A.rref()
    assert Ar == DomainMatrix([[QQ(1), QQ(0)], [QQ(0), QQ(1)]], (2, 2), QQ)
    assert pivots == (0, 1)

    A = DomainMatrix([[QQ(0), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Ar, pivots = A.rref()
    assert Ar == DomainMatrix([[QQ(1), QQ(0)], [QQ(0), QQ(1)]], (2, 2), QQ)
    assert pivots == (0, 1)

    A = DomainMatrix([[QQ(0), QQ(2)], [QQ(0), QQ(4)]], (2, 2), QQ)
    Ar, pivots = A.rref()
    assert Ar == DomainMatrix([[QQ(0), QQ(1)], [QQ(0), QQ(0)]], (2, 2), QQ)
    assert pivots == (1,)

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    raises(ValueError, lambda: Az.rref())


def test_DomainMatrix_nullspace():
    A = DomainMatrix([[QQ(1), QQ(1)], [QQ(1), QQ(1)]], (2, 2), QQ)
    Anull = DomainMatrix([[QQ(-1), QQ(1)]], (1, 2), QQ)
    assert A.nullspace() == Anull

    Az = DomainMatrix([[ZZ(1), ZZ(1)], [ZZ(1), ZZ(1)]], (2, 2), ZZ)
    raises(ValueError, lambda: Az.nullspace())


def test_DomainMatrix_solve():
    # XXX: Maybe the _solve method should be changed...
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(2), QQ(4)]], (2, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    particular = DomainMatrix([[1, 0]], (1, 2), QQ)
    nullspace = DomainMatrix([[-2, 1]], (1, 2), QQ)
    assert A._solve(b) == (particular, nullspace)

    b3 = DomainMatrix([[QQ(1)], [QQ(1)], [QQ(1)]], (3, 1), QQ)
    raises(ShapeError, lambda: A._solve(b3))

    bz = DomainMatrix([[ZZ(1)], [ZZ(1)]], (2, 1), ZZ)
    raises(ValueError, lambda: A._solve(bz))


def test_DomainMatrix_inv():
    """
    Test the inversion of a DomainMatrix.
    
    Parameters:
    - A (DomainMatrix): The input matrix for which the inverse is to be computed.
    
    Returns:
    - DomainMatrix: The inverse of the input matrix if it is invertible. Raises ValueError if the matrix is not square, NonInvertibleMatrixError if the matrix is singular, or NonSquareMatrixError if the matrix is not a square matrix.
    
    Examples:
    - A = DomainMatrix([], (0, 0), QQ) should return A
    """

    A = DomainMatrix([], (0, 0), QQ)
    assert A.inv() == A

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    Ainv = DomainMatrix([[QQ(-2), QQ(1)], [QQ(3, 2), QQ(-1, 2)]], (2, 2), QQ)
    assert A.inv() == Ainv

    Az = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    raises(ValueError, lambda: Az.inv())

    Ans = DomainMatrix([[QQ(1), QQ(2)]], (1, 2), QQ)
    raises(NonSquareMatrixError, lambda: Ans.inv())

    Aninv = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(6)]], (2, 2), QQ)
    raises(NonInvertibleMatrixError, lambda: Aninv.inv())


def test_DomainMatrix_det():
    A = DomainMatrix([], (0, 0), ZZ)
    assert A.det() == 1

    A = DomainMatrix([[1]], (1, 1), ZZ)
    assert A.det() == 1

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A.det() == ZZ(-2)

    A = DomainMatrix([[ZZ(1), ZZ(2), ZZ(3)], [ZZ(1), ZZ(2), ZZ(4)], [ZZ(1), ZZ(3), ZZ(5)]], (3, 3), ZZ)
    assert A.det() == ZZ(-1)

    A = DomainMatrix([[ZZ(1), ZZ(2), ZZ(3)], [ZZ(1), ZZ(2), ZZ(4)], [ZZ(1), ZZ(2), ZZ(5)]], (3, 3), ZZ)
    assert A.det() == ZZ(0)

    Ans = DomainMatrix([[QQ(1), QQ(2)]], (1, 2), QQ)
    raises(NonSquareMatrixError, lambda: Ans.det())

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    assert A.det() == QQ(-2)


def test_DomainMatrix_lu():
    """
    Compute the LU decomposition of a DomainMatrix.
    
    This function computes the LU decomposition of a given DomainMatrix. The LU
    decomposition expresses the matrix as the product of a lower triangular matrix
    (L) and an upper triangular matrix (U). The function also returns the sequence
    of row swaps performed during the decomposition.
    
    Parameters:
    A (DomainMatrix): The input matrix to be decomposed.
    
    Returns:
    (L, U, swaps): A tuple where L is the lower triangular matrix, U
    """

    A = DomainMatrix([], (0, 0), QQ)
    assert A.lu() == (A, A, [])

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    L = DomainMatrix([[QQ(1), QQ(0)], [QQ(3), QQ(1)]], (2, 2), QQ)
    U = DomainMatrix([[QQ(1), QQ(2)], [QQ(0), QQ(-2)]], (2, 2), QQ)
    swaps = []
    assert A.lu() == (L, U, swaps)

    A = DomainMatrix([[QQ(0), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    L = DomainMatrix([[QQ(1), QQ(0)], [QQ(0), QQ(1)]], (2, 2), QQ)
    U = DomainMatrix([[QQ(3), QQ(4)], [QQ(0), QQ(2)]], (2, 2), QQ)
    swaps = [(0, 1)]
    assert A.lu() == (L, U, swaps)

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(2), QQ(4)]], (2, 2), QQ)
    L = DomainMatrix([[QQ(1), QQ(0)], [QQ(2), QQ(1)]], (2, 2), QQ)
    U = DomainMatrix([[QQ(1), QQ(2)], [QQ(0), QQ(0)]], (2, 2), QQ)
    swaps = []
    assert A.lu() == (L, U, swaps)

    A = DomainMatrix([[QQ(0), QQ(2)], [QQ(0), QQ(4)]], (2, 2), QQ)
    L = DomainMatrix([[QQ(1), QQ(0)], [QQ(0), QQ(1)]], (2, 2), QQ)
    U = DomainMatrix([[QQ(0), QQ(2)], [QQ(0), QQ(4)]], (2, 2), QQ)
    swaps = []
    assert A.lu() == (L, U, swaps)

    A = DomainMatrix([[QQ(1), QQ(2), QQ(3)], [QQ(4), QQ(5), QQ(6)]], (2, 3), QQ)
    L = DomainMatrix([[QQ(1), QQ(0)], [QQ(4), QQ(1)]], (2, 2), QQ)
    U = DomainMatrix([[QQ(1), QQ(2), QQ(3)], [QQ(0), QQ(-3), QQ(-6)]], (2, 3), QQ)
    swaps = []
    assert A.lu() == (L, U, swaps)

    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]], (3, 2), QQ)
    L = DomainMatrix([
        [QQ(1), QQ(0), QQ(0)],
        [QQ(3), QQ(1), QQ(0)],
        [QQ(5), QQ(2), QQ(1)]], (3, 3), QQ)
    U = DomainMatrix([[QQ(1), QQ(2)], [QQ(0), QQ(-2)], [QQ(0), QQ(0)]], (3, 2), QQ)
    swaps = []
    assert A.lu() == (L, U, swaps)

    A = [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 1, 2]]
    L = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 1]]
    U = [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
    to_dom = lambda rows, dom: [[dom(e) for e in row] for row in rows]
    A = DomainMatrix(to_dom(A, QQ), (4, 4), QQ)
    L = DomainMatrix(to_dom(L, QQ), (4, 4), QQ)
    U = DomainMatrix(to_dom(U, QQ), (4, 4), QQ)
    assert A.lu() == (L, U, [])

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    raises(ValueError, lambda: A.lu())


def test_DomainMatrix_lu_solve():
    # Base case
    A = b = x = DomainMatrix([], (0, 0), QQ)
    assert A.lu_solve(b) == x

    # Basic example
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    x = DomainMatrix([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    assert A.lu_solve(b) == x

    # Example with swaps
    A = DomainMatrix([[QQ(0), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    x = DomainMatrix([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    assert A.lu_solve(b) == x

    # Non-invertible
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(2), QQ(4)]], (2, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)]], (2, 1), QQ)
    raises(NonInvertibleMatrixError, lambda: A.lu_solve(b))

    # Overdetermined, consistent
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]], (3, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)], [QQ(3)]], (3, 1), QQ)
    x = DomainMatrix([[QQ(0)], [QQ(1, 2)]], (2, 1), QQ)
    assert A.lu_solve(b) == x

    # Overdetermined, inconsistent
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]], (3, 2), QQ)
    b = DomainMatrix([[QQ(1)], [QQ(2)], [QQ(4)]], (3, 1), QQ)
    raises(NonInvertibleMatrixError, lambda: A.lu_solve(b))

    # Underdetermined
    A = DomainMatrix([[QQ(1), QQ(2)]], (1, 2), QQ)
    b = DomainMatrix([[QQ(1)]], (1, 1), QQ)
    raises(NotImplementedError, lambda: A.lu_solve(b))

    # Non-field
    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    b = DomainMatrix([[ZZ(1)], [ZZ(2)]], (2, 1), ZZ)
    raises(ValueError, lambda: A.lu_solve(b))

    # Shape mismatch
    A = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)]], (2, 2), QQ)
    b = DomainMatrix([[QQ(1), QQ(2)]], (1, 2), QQ)
    raises(ShapeError, lambda: A.lu_solve(b))


def test_DomainMatrix_charpoly():
    """
    Compute the characteristic polynomial of a DomainMatrix.
    
    This function calculates the characteristic polynomial of a given DomainMatrix.
    
    Parameters:
    A (DomainMatrix): The input matrix for which the characteristic polynomial is to be computed.
    
    Returns:
    list: A list of coefficients representing the characteristic polynomial of the input matrix.
    
    Raises:
    NonSquareMatrixError: If the input matrix is not square.
    """

    A = DomainMatrix([], (0, 0), ZZ)
    assert A.charpoly() == [ZZ(1)]

    A = DomainMatrix([[1]], (1, 1), ZZ)
    assert A.charpoly() == [ZZ(1), ZZ(-1)]

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A.charpoly() == [ZZ(1), ZZ(-5), ZZ(-2)]

    A = DomainMatrix([[ZZ(1), ZZ(2), ZZ(3)], [ZZ(4), ZZ(5), ZZ(6)], [ZZ(7), ZZ(8), ZZ(9)]], (3, 3), ZZ)
    assert A.charpoly() == [ZZ(1), ZZ(-15), ZZ(-18), ZZ(0)]

    Ans = DomainMatrix([[QQ(1), QQ(2)]], (1, 2), QQ)
    raises(NonSquareMatrixError, lambda: Ans.charpoly())


def test_DomainMatrix_eye():
    """
    Test the creation of a 3x3 identity matrix using the DomainMatrix.eye function with the domain set to QQ (rational numbers). The resulting DomainMatrix object should have the correct representation, shape, and domain.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Attributes:
    - A (DomainMatrix): The resulting 3x3 identity matrix with entries in the field of rational numbers (QQ).
    - A.rep (SDM): The sparse domain matrix representation of A.
    - A.shape (
    """

    A = DomainMatrix.eye(3, QQ)
    assert A.rep == SDM.eye(3, QQ)
    assert A.shape == (3, 3)
    assert A.domain == QQ


def test_DomainMatrix_zeros():
    A = DomainMatrix.zeros((1, 2), QQ)
    assert A.rep == SDM.zeros((1, 2), QQ)
    assert A.shape == (1, 2)
    assert A.domain == QQ


def test_DomainMatrix_ones():
    A = DomainMatrix.ones((2, 3), QQ)
    assert A.rep == DDM.ones((2, 3), QQ)
    assert A.shape == (2, 3)
    assert A.domain == QQ


def test_DomainMatrix_diag():
    """
    Create a diagonal DomainMatrix.
    
    Args:
    elements (list): A list of elements for the diagonal.
    domain (Domain): The domain of the resulting DomainMatrix.
    shape (tuple, optional): The shape of the resulting DomainMatrix.
    Defaults to (2, 2).
    
    Returns:
    DomainMatrix: A diagonal DomainMatrix with the specified elements and domain.
    """

    A = DomainMatrix({0:{0:ZZ(2)}, 1:{1:ZZ(3)}}, (2, 2), ZZ)
    assert DomainMatrix.diag([ZZ(2), ZZ(3)], ZZ) == A

    A = DomainMatrix({0:{0:ZZ(2)}, 1:{1:ZZ(3)}}, (3, 4), ZZ)
    assert DomainMatrix.diag([ZZ(2), ZZ(3)], ZZ, (3, 4)) == A


def test_DomainMatrix_hstack():
    A = DomainMatrix([[ZZ(1)], [ZZ(2)]], (2, 1), ZZ)
    B = DomainMatrix([[QQ(3), QQ(4)], [QQ(5), QQ(6)]], (2, 2), QQ)
    AB = DomainMatrix([[QQ(1), QQ(3), QQ(4)], [QQ(2), QQ(5), QQ(6)]], (2, 3), QQ)
    assert A.hstack(B) == AB


def test_DomainMatrix_vstack():
    A = DomainMatrix([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    B = DomainMatrix([[QQ(3), QQ(4)], [QQ(5), QQ(6)]], (2, 2), QQ)
    AB = DomainMatrix([[QQ(1), QQ(2)], [QQ(3), QQ(4)], [QQ(5), QQ(6)]], (3, 2), QQ)
    assert A.vstack(B) == AB


def test_DomainMatrix_applyfunc():
    A = DomainMatrix([[ZZ(1), ZZ(2)]], (1, 2), ZZ)
    B = DomainMatrix([[ZZ(2), ZZ(4)]], (1, 2), ZZ)
    assert A.applyfunc(lambda x: 2*x) == B


def test_DomainMatrix_scalarmul():
    """
    Multiply a DomainMatrix by a scalar.
    
    Parameters:
    A (DomainMatrix): The matrix to be multiplied.
    lamda (DomainScalar or int): The scalar to multiply the matrix by.
    
    Returns:
    DomainMatrix: The result of the scalar multiplication.
    
    Examples:
    >>> A = DomainMatrix([[1, 2], [3, 4]], (2, 2), ZZ)
    >>> lamda = DomainScalar(3/2, QQ)
    >>> A * lamda
    """

    A = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    lamda = DomainScalar(QQ(3)/QQ(2), QQ)
    assert A * lamda == DomainMatrix([[QQ(3, 2), QQ(3)], [QQ(9, 2), QQ(6)]], (2, 2), QQ)
    assert A * 2 == DomainMatrix([[ZZ(2), ZZ(4)], [ZZ(6), ZZ(8)]], (2, 2), ZZ)
    assert A * DomainScalar(ZZ(0), ZZ) == DomainMatrix([[ZZ(0)]*2]*2, (2, 2), ZZ)
    assert A * DomainScalar(ZZ(1), ZZ) == A

    raises(TypeError, lambda: A * 1.5)


def test_DomainMatrix_truediv():
    A = DomainMatrix.from_Matrix(Matrix([[1, 2], [3, 4]]))
    lamda = DomainScalar(QQ(3)/QQ(2), QQ)
    assert A / lamda == DomainMatrix({0: {0: QQ(2, 3), 1: QQ(4, 3)}, 1: {0: QQ(2), 1: QQ(8, 3)}}, (2, 2), QQ)
    b = DomainScalar(ZZ(1), ZZ)
    assert A / b == DomainMatrix({0: {0: QQ(1), 1: QQ(2)}, 1: {0: QQ(3), 1: QQ(4)}}, (2, 2), QQ)

    assert A / 1 == DomainMatrix({0: {0: QQ(1), 1: QQ(2)}, 1: {0: QQ(3), 1: QQ(4)}}, (2, 2), QQ)
    assert A / 2 == DomainMatrix({0: {0: QQ(1, 2), 1: QQ(1)}, 1: {0: QQ(3, 2), 1: QQ(2)}}, (2, 2), QQ)

    raises(ZeroDivisionError, lambda: A / 0)
    raises(TypeError, lambda: A / 1.5)
    raises(ZeroDivisionError, lambda: A / DomainScalar(ZZ(0), ZZ))


def test_DomainMatrix_getitem():
    dM = DomainMatrix([
        [ZZ(1), ZZ(2), ZZ(3)],
        [ZZ(4), ZZ(5), ZZ(6)],
        [ZZ(7), ZZ(8), ZZ(9)]], (3, 3), ZZ)

    assert dM[1:,:-2] == DomainMatrix([[ZZ(4)], [ZZ(7)]], (2, 1), ZZ)
    assert dM[2,:-2] == DomainMatrix([[ZZ(7)]], (1, 1), ZZ)
    assert dM[:-2,:-2] == DomainMatrix([[ZZ(1)]], (1, 1), ZZ)
    assert dM[:-1,0:2] == DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(4), ZZ(5)]], (2, 2), ZZ)
    assert dM[:, -1] == DomainMatrix([[ZZ(3)], [ZZ(6)], [ZZ(9)]], (3, 1), ZZ)
    assert dM[-1, :] == DomainMatrix([[ZZ(7), ZZ(8), ZZ(9)]], (1, 3), ZZ)
    assert dM[::-1, :] == DomainMatrix([
                            [ZZ(7), ZZ(8), ZZ(9)],
                            [ZZ(4), ZZ(5), ZZ(6)],
                            [ZZ(1), ZZ(2), ZZ(3)]], (3, 3), ZZ)

    raises(IndexError, lambda: dM[4, :-2])
    raises(IndexError, lambda: dM[:-2, 4])

    assert dM[1, 2] == DomainScalar(ZZ(6), ZZ)
    assert dM[-2, 2] == DomainScalar(ZZ(6), ZZ)
    assert dM[1, -2] == DomainScalar(ZZ(5), ZZ)
    assert dM[-1, -3] == DomainScalar(ZZ(7), ZZ)

    raises(IndexError, lambda: dM[3, 3])
    raises(IndexError, lambda: dM[1, 4])
    raises(IndexError, lambda: dM[-1, -4])

    dM = DomainMatrix({0: {0: ZZ(1)}}, (10, 10), ZZ)
    assert dM[5, 5] == DomainScalar(ZZ(0), ZZ)
    assert dM[0, 0] == DomainScalar(ZZ(1), ZZ)

    dM = DomainMatrix({1: {0: 1}}, (2,1), ZZ)
    assert dM[0:, 0] == DomainMatrix({1: {0: 1}}, (2, 1), ZZ)
    raises(IndexError, lambda: dM[3, 0])

    dM = DomainMatrix({2: {2: ZZ(1)}, 4: {4: ZZ(1)}}, (5, 5), ZZ)
    assert dM[:2,:2] == DomainMatrix({}, (2, 2), ZZ)
    assert dM[2:,2:] == DomainMatrix({0: {0: 1}, 2: {2: 1}}, (3, 3), ZZ)
    assert dM[3:,3:] == DomainMatrix({1: {1: 1}}, (2, 2), ZZ)
    assert dM[2:, 6:] == DomainMatrix({}, (3, 0), ZZ)
