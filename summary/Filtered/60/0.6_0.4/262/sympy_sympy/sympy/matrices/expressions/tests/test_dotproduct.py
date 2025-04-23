from sympy.core.expr import unchanged
from sympy.core.mul import Mul
from sympy.matrices import Matrix
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.matrices.expressions.dotproduct import DotProduct
from sympy.utilities.pytest import raises


A = Matrix(3, 1, [1, 2, 3])
B = Matrix(3, 1, [1, 3, 5])
C = Matrix(4, 1, [1, 2, 4, 5])
D = Matrix(2, 2, [1, 2, 3, 4])

def test_docproduct():
    assert DotProduct(A, B).doit() == 22
    assert DotProduct(A.T, B).doit() == 22
    assert DotProduct(A, B.T).doit() == 22
    assert DotProduct(A.T, B.T).doit() == 22

    raises(TypeError, lambda: DotProduct(1, A))
    raises(TypeError, lambda: DotProduct(A, 1))
    raises(TypeError, lambda: DotProduct(A, D))
    raises(TypeError, lambda: DotProduct(D, A))

    raises(TypeError, lambda: DotProduct(B, C).doit())

def test_dotproduct_symbolic():
    """
    Test the symbolic dot product of two matrix expressions.
    
    Parameters
    ----------
    A : MatrixSymbol
    A 3x1 matrix symbol.
    B : MatrixSymbol
    A 3x1 matrix symbol.
    
    Returns
    -------
    dot : DotProduct
    The symbolic dot product of A and B.
    
    Notes
    -----
    The function checks if the dot product is scalar and verifies that the
    dot product is not altered by scalar multiplication. It also demonstrates
    how the dot product interacts with matrix expressions.
    """

    A = MatrixSymbol('A', 3, 1)
    B = MatrixSymbol('B', 3, 1)

    dot = DotProduct(A, B)
    assert dot.is_scalar == True
    assert unchanged(Mul, 2, dot)
    # XXX Fix forced evaluation for arithmetics with matrix expressions
    assert dot * A == (A[0, 0]*B[0, 0] + A[1, 0]*B[1, 0] + A[2, 0]*B[2, 0])*A
