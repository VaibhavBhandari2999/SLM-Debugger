from sympy.core.expr import unchanged
from sympy.core.symbol import Symbol, symbols
from sympy.matrices.immutable import ImmutableDenseMatrix
from sympy.matrices.expressions.companion import CompanionMatrix
from sympy.polys.polytools import Poly
from sympy.testing.pytest import raises


def test_creation():
    x = Symbol('x')
    y = Symbol('y')
    raises(ValueError, lambda: CompanionMatrix(1))
    raises(ValueError, lambda: CompanionMatrix(Poly([1], x)))
    raises(ValueError, lambda: CompanionMatrix(Poly([2, 1], x)))
    raises(ValueError, lambda: CompanionMatrix(Poly(x*y, [x, y])))
    unchanged(CompanionMatrix, Poly([1, 2, 3], x))


def test_shape():
    """
    Generate a companion matrix for a polynomial.
    
    This function creates a companion matrix for a given polynomial in the variable x.
    The polynomial is represented by its coefficients, which are provided as symbols.
    
    Parameters:
    poly (Poly): A polynomial in the variable x, represented as a Poly object.
    
    Returns:
    Matrix: The companion matrix of the given polynomial, as a SymPy Matrix object.
    
    Example:
    >>> c0, c1, c2 = symbols('c0:3')
    >>> x
    """

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
    
    This function takes a polynomial and returns the corresponding companion matrix
    in explicit form. The polynomial is represented by its coefficients, and the
    function constructs the companion matrix based on these coefficients.
    
    Parameters:
    poly (Poly): The polynomial for which the companion matrix is to be generated.
    
    Returns:
    ImmutableDenseMatrix: The companion matrix in explicit form.
    """

    c0, c1, c2 = symbols('c0:3')
    x = Symbol('x')
    assert CompanionMatrix(Poly([1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([-c0])
    assert CompanionMatrix(Poly([1, c1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([[0, -c0], [1, -c1]])
    assert CompanionMatrix(Poly([1, c2, c1, c0], x)).as_explicit() == \
        ImmutableDenseMatrix([[0, 0, -c0], [1, 0, -c1], [0, 1, -c2]])
