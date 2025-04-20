from sympy.testing.pytest import raises

from sympy.core.symbol import S
from sympy.polys import ZZ, QQ
from sympy.polys.matrices.domainscalar import DomainScalar
from sympy.polys.matrices.domainmatrix import DomainMatrix


def test_DomainScalar___new__():
    raises(TypeError, lambda: DomainScalar(ZZ(1), QQ))
    raises(TypeError, lambda: DomainScalar(ZZ(1), 1))


def test_DomainScalar_new():
    A = DomainScalar(ZZ(1), ZZ)
    B = A.new(ZZ(4), ZZ)
    assert B == DomainScalar(ZZ(4), ZZ)


def test_DomainScalar_repr():
    A = DomainScalar(ZZ(1), ZZ)
    assert repr(A) in {'1', 'mpz(1)'}


def test_DomainScalar_from_sympy():
    """
    Generate a DomainScalar instance from a SymPy expression.
    
    This function takes a SymPy expression and converts it into a DomainScalar object.
    
    Parameters:
    expr (sympy.Expr): The SymPy expression to be converted.
    
    Returns:
    DomainScalar: A DomainScalar object corresponding to the given SymPy expression.
    
    Example:
    >>> from sympy import S
    >>> from domain_scalar import DomainScalar, ZZ
    >>> expr = S(1)
    >>> B = test_DomainScalar_from_sympy(expr)
    """

    expr = S(1)
    B = DomainScalar.from_sympy(expr)
    assert B == DomainScalar(ZZ(1), ZZ)


def test_DomainScalar_to_sympy():
    """
    Convert a DomainScalar object to a SymPy expression.
    
    This function takes a DomainScalar object and converts it into a SymPy expression. The resulting expression is an integer.
    
    Parameters:
    B (DomainScalar): The DomainScalar object to be converted.
    
    Returns:
    sympy.core.numbers.Integer: The SymPy integer representation of the DomainScalar object.
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
    """
    Unify the domains of two DomainScalar objects.
    
    This function takes two DomainScalar objects, A and B, and unifies their domains to a common domain. The unified domain is the smallest domain that can contain both original domains.
    
    Parameters:
    A (DomainScalar): The first DomainScalar object.
    B (DomainScalar): The second DomainScalar object.
    
    Returns:
    tuple: A tuple containing the unified DomainScalar objects (A, B) with the same domain.
    
    Example:
    >>> A = DomainScalar(Z
    """

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
    """
    Divide a DomainScalar by another DomainScalar or an integer.
    
    Parameters:
    - A (DomainScalar): The dividend, an instance of DomainScalar with an integer value and a domain.
    - B (DomainScalar or int): The divisor, an instance of DomainScalar with an integer value and a domain, or an integer.
    
    Returns:
    - DomainScalar: The result of the division, an instance of DomainScalar with the quotient value and the common domain of A and B.
    
    Raises:
    - TypeError:
    """

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
    
    This function performs the division and modulo operations on two DomainScalar objects.
    
    Parameters:
    A (DomainScalar): The dividend.
    B (DomainScalar): The divisor.
    
    Returns:
    tuple: A tuple containing the quotient and remainder as DomainScalar objects.
    
    Raises:
    TypeError: If the divisor is not a DomainScalar object or is not of the same domain type.
    """

    A = DomainScalar(ZZ(5), ZZ)
    B = DomainScalar(QQ(2), QQ)
    assert divmod(A, B) == (DomainScalar(QQ(5, 2), QQ), DomainScalar(QQ(0), QQ))
    C = DomainScalar(ZZ(2), ZZ)
    assert divmod(A, C) == (DomainScalar(ZZ(2), ZZ), DomainScalar(ZZ(1), ZZ))

    raises(TypeError, lambda: divmod(A, 1.5))


def test_DomainScalar_pow():
    """
    Raise a DomainScalar object to a power.
    
    Parameters:
    - A (DomainScalar): The base DomainScalar object.
    - exponent (int): The exponent to which the base is raised.
    
    Returns:
    - DomainScalar: The result of raising the base to the specified power.
    
    Raises:
    - TypeError: If the exponent is not an integer.
    """

    A = DomainScalar(ZZ(-5), ZZ)
    B = A**(2)
    assert B == DomainScalar(ZZ(25), ZZ)

    raises(TypeError, lambda: A**(1.5))


def test_DomainScalar_pos():
    A = DomainScalar(QQ(2), QQ)
    B = DomainScalar(QQ(2), QQ)
    assert  +A == B


def test_DomainScalar_eq():
    A = DomainScalar(QQ(2), QQ)
    assert A == A
    B = DomainScalar(ZZ(-5), ZZ)
    assert A != B
    C = DomainScalar(ZZ(2), ZZ)
    assert A != C
    D = [1]
    assert A != D


def test_DomainScalar_isZero():
    """
    Test if a DomainScalar object is zero.
    
    Parameters:
    - A (DomainScalar): The DomainScalar object to test.
    
    Returns:
    - bool: True if the DomainScalar object is zero, False otherwise.
    
    Example usage:
    >>> A = DomainScalar(ZZ(0), ZZ)
    >>> test_DomainScalar_isZero(A)
    True
    >>> B = DomainScalar(ZZ(1), ZZ)
    >>> test_DomainScalar_isZero(B)
    False
    """

    A = DomainScalar(ZZ(0), ZZ)
    assert A.is_zero() == True
    B = DomainScalar(ZZ(1), ZZ)
    assert B.is_zero() == False


def test_DomainScalar_isOne():
    A = DomainScalar(ZZ(1), ZZ)
    assert A.is_one() == True
    B = DomainScalar(ZZ(0), ZZ)
    assert B.is_one() == False
