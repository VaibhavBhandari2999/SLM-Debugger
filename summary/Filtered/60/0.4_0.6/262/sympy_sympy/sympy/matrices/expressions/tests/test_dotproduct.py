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
    Test the dot product of matrices and vectors.
    
    Parameters:
    - A, B, C, D: Matrices or vectors on which the dot product is to be tested.
    
    Returns:
    - The result of the dot product as an integer.
    
    Raises:
    - TypeError: If the input arguments are not compatible for dot product calculation.
    
    Examples:
    - test_docproduct() verifies the dot product of matrices and vectors and checks for type errors.
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
    
    Parameters:
    A (MatrixSymbol): A 3x1 symbolic matrix.
    B (MatrixSymbol): A 3x1 symbolic matrix.
    
    Returns:
    dot (DotProduct): The dot product of A and B, which is a scalar.
    unchanged (function): A function that returns the input unchanged.
    dot * A (Expression): The result of the dot product of A and B multiplied by A.
    """

    A = MatrixSymbol('A', 3, 1)
    B = MatrixSymbol('B', 3, 1)

    dot = DotProduct(A, B)
    assert dot.is_scalar == True
    assert unchanged(Mul, 2, dot)
    # XXX Fix forced evaluation for arithmetics with matrix expressions
    assert dot * A == (A[0, 0]*B[0, 0] + A[1, 0]*B[1, 0] + A[2, 0]*B[2, 0])*A
