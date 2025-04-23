from sympy.core.expr import unchanged
from sympy.core.symbol import Symbol, symbols
from sympy.matrices.immutable import ImmutableDenseMatrix
from sympy.matrices.expressions.companion import CompanionMatrix
from sympy.polys.polytools import Poly
from sympy.testing.pytest import raises


def test_creation():
    """
    Create and validate a companion matrix.
    
    This function tests the creation of a companion matrix with various inputs and raises appropriate errors for invalid inputs.
    
    Parameters:
    None (The function uses predefined symbolic variables and polynomials)
    
    Returns:
    None (The function uses assertions and raises exceptions to validate the input)
    
    Raises:
    ValueError: If the input polynomial is invalid for creating a companion matrix
    
    Examples:
    >>> test_creation()
    # The function should pass without raising any exceptions for valid inputs and raise ValueError for
    """

    x = Symbol('x')
    y = Symbol('y')
    raises(ValueError, lambda: CompanionMatrix(1))
    raises(ValueError, lambda: CompanionMatrix(Poly([1], x)))
    raises(ValueError, lambda: CompanionMatrix(Poly([2, 1], x)))
    raises(ValueError, lambda: CompanionMatrix(Poly(x*y, [x, y])))
    assert unchanged(CompanionMatrix, Poly([1, 2, 3], x))


def test_shape():
    c0, c1, c2 = symbols('c0:3')
    x = Symbol('x')
    assert CompanionMatrix(Poly([1, c0], x)).shape == (1, 1)
    assert CompanionMatrix(Poly([1, c1, c0], x)).shape == (2, 2)
    assert CompanionMatrix(Poly([1, c2, c1, c0], x)).shape == (3, 3)


def test_entry():
    c0, c1, c2 = symbols('c0:3')
    x = Symbol('x')
    A = CompanionMatrix(Poly([1, c2, c1, c0], x))
    assert A[0, 0] == 0
    assert A[1, 0] == 1
    assert A[1, 1] == 0
    assert A[2, 1] == 1
    assert A[0, 2] == -c0
    assert A[1, 2] == -c1
    assert A[2, 2] == -c2


def test_as_explicit():
    """
    Generate the explicit form of a companion matrix.
    
    Parameters:
    c0, c1, c2 (Symbol): Coefficients of the polynomial.
    x (Symbol): Symbol for the polynomial variable.
    
    Returns:
    ImmutableDenseMatrix: The explicit form of the companion matrix.
    """

    c0, c1, c2 = symbols('c0:3')
    x = Symbol('x')
    assert CompanionMatrix(Poly([1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([-c0])
    assert CompanionMatrix(Poly([1, c1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([[0, -c0], [1, -c1]])
    assert CompanionMatrix(Poly([1, c2, c1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([[0, 0, -c0], [1, 0, -c1], [0, 1, -c2]])
