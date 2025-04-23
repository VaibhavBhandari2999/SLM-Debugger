from sympy.testing.pytest import raises

from sympy.core.symbol import S
from sympy.polys import ZZ, QQ
from sympy.polys.matrices.domainscalar import DomainScalar
from sympy.polys.matrices.domainmatrix import DomainMatrix


def test_DomainScalar___new__():
    raises(TypeError, lambda: DomainScalar(ZZ(1), QQ))
    raises(TypeError, lambda: DomainScalar(ZZ(1), 1))


def test_DomainScalar_new():
    """
    Create a new DomainScalar instance with the specified value and domain.
    
    This function initializes a new DomainScalar object with the given value and domain.
    
    Parameters:
    value (int): The value to be assigned to the DomainScalar instance.
    domain (Ring): The domain in which the value exists.
    
    Returns:
    DomainScalar: A new DomainScalar instance with the specified value and domain.
    """

    A = DomainScalar(ZZ(1), ZZ)
    B = A.new(ZZ(4), ZZ)
    assert B == DomainScalar(ZZ(4), ZZ)


def test_DomainScalar_repr():
    A = DomainScalar(ZZ(1), ZZ)
    assert repr(A) in {'1', 'mpz(1)'}


def test_DomainScalar_from_sympy():
    """
    Create a DomainScalar object from a SymPy expression.
    
    This function takes a SymPy expression and converts it into a DomainScalar object with the appropriate domain.
    
    Parameters:
    expr (SymPy expression): The SymPy expression to be converted.
    
    Returns:
    DomainScalar: A DomainScalar object representing the given SymPy expression with the corresponding domain.
    
    Example:
    >>> from sympy import S
    >>> from domain_scalar import DomainScalar, ZZ
    >>> expr = S(1)
    >>> B = test_DomainScalar
    """

    expr = S(1)
    B = DomainScalar.from_sympy(expr)
    assert B == DomainScalar(ZZ(1), ZZ)


def test_DomainScalar_to_sympy():
    """
    Convert a DomainScalar object to a SymPy expression.
    
    This function takes a DomainScalar object and converts it to a SymPy expression.
    
    Parameters:
    B (DomainScalar): The DomainScalar object to be converted.
    
    Returns:
    sympy.core.numbers.Integer: The SymPy integer equivalent of the DomainScalar object.
    
    Example:
    >>> B = DomainScalar(ZZ(1), ZZ)
    >>> expr = B.to_sympy()
    >>> expr.is_Integer and expr == 1
    True
    """

    B = DomainScalar(ZZ(1), ZZ)
    expr = B.to_sympy()
    assert expr.is_Integer and expr == 1


def test_DomainScalar_to_domain():
    A = DomainScalar(ZZ(1), ZZ)
    B = A.to_domain(QQ)
    assert B == DomainScalar(QQ(1), QQ)


def test_DomainScalar_convert_to():
    A = DomainScalar(ZZ(1), ZZ)
    B = A.convert_to(QQ)
    assert B == DomainScalar(QQ(1), QQ)


def test_DomainScalar_unify():
    A = DomainScalar(ZZ(1), ZZ)
    B = DomainScalar(QQ(2), QQ)
    A, B = A.unify(B)
    assert A.domain == B.domain == QQ


def test_DomainScalar_add():
    A = DomainScalar(ZZ(1), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert A + B == DomainScalar(QQ(3), QQ)

    raises(TypeError, lambda: A + 1.5)

def test_DomainScalar_sub():
    A = DomainScalar(ZZ(1), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert A - B == DomainScalar(QQ(-1), QQ)

    raises(TypeError, lambda: A - 1.5)

def test_DomainScalar_mul():
    A = DomainScalar(ZZ(1), ZZ)
    B = DomainScalar(QQ(2), QQ)
    dm = DomainMatrix([[ZZ(1), ZZ(2)], [ZZ(3), ZZ(4)]], (2, 2), ZZ)
    assert A * B == DomainScalar(QQ(2), QQ)
    assert A * dm == dm
    assert B * 2 == DomainScalar(QQ(4), QQ)

    raises(TypeError, lambda: A * 1.5)


def test_DomainScalar_floordiv():
    A = DomainScalar(ZZ(-5), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert A // B == DomainScalar(QQ(-5, 2), QQ)
    C = DomainScalar(ZZ(2), ZZ)
    assert A // C == DomainScalar(ZZ(-3), ZZ)

    raises(TypeError, lambda: A // 1.5)


def test_DomainScalar_mod():
    A = DomainScalar(ZZ(5), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert A % B == DomainScalar(QQ(0), QQ)
    C = DomainScalar(ZZ(2), ZZ)
    assert A % C == DomainScalar(ZZ(1), ZZ)

    raises(TypeError, lambda: A % 1.5)


def test_DomainScalar_divmod():
    """
    Divide and modulo operation for DomainScalar objects.
    
    Parameters:
    A (DomainScalar): The dividend, an instance of DomainScalar with an integer value and a coefficient domain.
    B (DomainScalar): The divisor, an instance of DomainScalar with a rational value and a coefficient domain.
    
    Returns:
    A tuple containing two DomainScalar objects: the quotient and the remainder.
    
    Raises:
    TypeError: If the divisor is not an instance of DomainScalar or is not an integer.
    
    Examples:
    >>> A = DomainScalar(Z
    """

    A = DomainScalar(ZZ(5), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert divmod(A, B) == (DomainScalar(QQ(5, 2), QQ), DomainScalar(QQ(0), QQ))
    C = DomainScalar(ZZ(2), ZZ)
    assert divmod(A, C) == (DomainScalar(ZZ(2), ZZ), DomainScalar(ZZ(1), ZZ))

    raises(TypeError, lambda: divmod(A, 1.5))


def test_DomainScalar_pow():
    A = DomainScalar(ZZ(-5), ZZ)
    B = A**(2)
    assert B == DomainScalar(ZZ(25), ZZ)

    raises(TypeError, lambda: A**(1.5))


def test_DomainScalar_pos():
    A = DomainScalar(QQ(2), QQ)
    B = DomainScalar(QQ(2), QQ)
    assert  +A == B


def test_DomainScalar_eq():
    """
    Test equality of DomainScalar objects.
    
    This function checks the equality of different DomainScalar objects based on their values and domains.
    
    Parameters:
    A (DomainScalar): First DomainScalar object to compare.
    B (DomainScalar): Second DomainScalar object to compare.
    C (DomainScalar): Third DomainScalar object to compare.
    D (list): A list for comparison, not a DomainScalar.
    
    Returns:
    bool: True if the objects are equal, False otherwise.
    """

    A = DomainScalar(QQ(2), QQ)
    assert A == A
    B = DomainScalar(ZZ(-5), ZZ)
    assert A != B
    C = DomainScalar(ZZ(2), ZZ)
    assert A != C
    D = [1]
    assert A != D


def test_DomainScalar_isZero():
    A = DomainScalar(ZZ(0), ZZ)
    assert A.is_zero() == True
    B = DomainScalar(ZZ(1), ZZ)
    assert B.is_zero() == False


def test_DomainScalar_isOne():
    A = DomainScalar(ZZ(1), ZZ)
    assert A.is_one() == True
    B = DomainScalar(ZZ(0), ZZ)
    assert B.is_one() == False
