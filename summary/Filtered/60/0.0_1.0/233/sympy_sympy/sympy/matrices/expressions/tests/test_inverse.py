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
    
    This function tests the inverse function for different matrix operations and properties. It checks for shape errors, verifies the inverse of a matrix, and ensures that the inverse of the inverse of a matrix is the original matrix. It also checks the multiplication and division of matrices and their inverses, as well as the simplification of matrix multiplications involving inverses. Additionally, it tests the evaluation of the inverse function using the `doit` method.
    
    Parameters
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
