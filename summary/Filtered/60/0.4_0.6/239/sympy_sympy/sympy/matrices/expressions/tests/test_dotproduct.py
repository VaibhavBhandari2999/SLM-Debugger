from sympy.matrices import Matrix
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
    A (Matrix): A matrix or vector.
    B (Matrix): Another matrix or vector.
    
    Returns:
    int: The result of the dot product.
    
    Raises:
    TypeError: If the input is not a matrix or vector, or if the dimensions are incompatible for the dot product.
    
    Examples:
    >>> test_docproduct()
    assert DotProduct(A, B).doit() == 22
    assert DotProduct(A.T, B).doit() ==
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
