from sympy.core import symbols, S
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
    Test the inverse of matrices and expressions involving matrices.
    
    This function checks the inverse of various matrices and matrix expressions.
    It raises ShapeError for non-square matrices or incompatible shapes for inverse operations.
    It also tests the inverse of matrix products and compositions, and ensures that the inverse
    of the inverse of a matrix is the original matrix. It verifies that the product of a matrix
    and its inverse is the identity matrix. It also tests the handling of scalar multiples of
    identity matrices and the simplification of matrix
    """

    raises(ShapeError, lambda: Inverse(A))
    raises(ShapeError, lambda: Inverse(A*B))

    assert Inverse(C).args == (C, S(-1))
    assert Inverse(C).shape == (n, n)
    assert Inverse(A*E).shape == (n, n)
    assert Inverse(E*A).shape == (m, m)
    assert Inverse(C).inverse() == C
    assert isinstance(Inverse(Inverse(C)), Inverse)

    assert Inverse(*Inverse(E*A).args) == Inverse(E*A)

    assert C.inverse().inverse() == C

    assert C.inverse()*C == Identity(C.rows)

    assert Identity(n).inverse() == Identity(n)
    assert (3*Identity(n)).inverse() == Identity(n)/3

    # Simplifies Muls if possible (i.e. submatrices are square)
    assert (C*D).inverse() == D.I*C.I
    # But still works when not possible
    assert isinstance((A*E).inverse(), Inverse)
    assert Inverse(C*D).doit(inv_expand=False) == Inverse(C*D)

    assert Inverse(eye(3)).doit() == eye(3)
    assert Inverse(eye(3)).doit(deep=False) == eye(3)


def test_refine():
    assert refine(C.I, Q.orthogonal(C)) == C.T
