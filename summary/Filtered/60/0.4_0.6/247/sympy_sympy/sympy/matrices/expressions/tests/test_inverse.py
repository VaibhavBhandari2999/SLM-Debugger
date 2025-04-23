from sympy.core import symbols
from sympy.matrices.expressions import MatrixSymbol, Inverse
from sympy.matrices import eye, Identity, ShapeError
from sympy.utilities.pytest import raises
from sympy import refine, Q

n, m, l = symbols('n m l', integer=True)
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)


def test_inverse():
    """
    Test the inverse function for various matrix operations and properties.
    
    This function checks the inverse function for different matrix operations and properties, including handling of non-square matrices, multiplication, and identity matrices. It also tests the inverse of the inverse, multiplication with the inverse, and simplification of expressions involving the inverse.
    
    Key Parameters:
    - A, B, C, D, E: Matrices used in the tests.
    - n, m: Dimensions of the matrices.
    
    Keywords:
    - Raises: ShapeError for non
    """

    raises(ShapeError, lambda: Inverse(A))
    raises(ShapeError, lambda: Inverse(A*B))

    assert Inverse(C).shape == (n, n)
    assert Inverse(A*E).shape == (n, n)
    assert Inverse(E*A).shape == (m, m)
    assert Inverse(C).inverse() == C
    assert isinstance(Inverse(Inverse(C)), Inverse)

    assert C.inverse().inverse() == C

    assert C.inverse()*C == Identity(C.rows)

    assert Identity(n).inverse() == Identity(n)
    assert (3*Identity(n)).inverse() == Identity(n)/3

    # Simplifies Muls if possible (i.e. submatrices are square)
    assert (C*D).inverse() == D.I*C.I
    # But still works when not possible
    assert isinstance((A*E).inverse(), Inverse)

    assert Inverse(eye(3)).doit() == eye(3)
    assert Inverse(eye(3)).doit(deep=False) == eye(3)


def test_refine():
    assert refine(C.I, Q.orthogonal(C)) == C.T
