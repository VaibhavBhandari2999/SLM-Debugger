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
    """
    Test the DotProduct function with various matrix inputs and operations. The function verifies the correct computation of the dot product for different matrix orientations and checks for type errors. It also demonstrates that the dot product is not commutative for non-square matrices.
    
    Parameters:
    A, B, C, D (Matrix): Input matrices for the dot product operations.
    
    Returns:
    None: The function asserts the correctness of the dot product calculations and raises TypeError for invalid inputs.
    
    Raises:
    TypeError: If the inputs
    """

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
    Test dot product of symbolic matrices.
    
    Parameters
    ----------
    A : MatrixSymbol
    A 3x1 symbolic matrix.
    B : MatrixSymbol
    A 3x1 symbolic matrix.
    
    Returns
    -------
    dot : DotProduct
    The dot product of A and B, which is a scalar.
    
    Notes
    -----
    The function checks if the dot product is a scalar and ensures that the
    dot product is not altered by multiplication with a scalar. It also
    handles arithmetic operations with matrix expressions.
    """

    A = MatrixSymbol('A', 3, 1)
    B = MatrixSymbol('B', 3, 1)

    dot = DotProduct(A, B)
    assert dot.is_scalar == True
    assert unchanged(Mul, 2, dot)
    # XXX Fix forced evaluation for arithmetics with matrix expressions
    assert dot * A == (A[0, 0]*B[0, 0] + A[1, 0]*B[1, 0] + A[2, 0]*B[2, 0])*A
