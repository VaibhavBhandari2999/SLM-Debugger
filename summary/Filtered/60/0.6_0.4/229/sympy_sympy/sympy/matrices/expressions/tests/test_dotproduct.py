from sympy.matrices import Matrix
from sympy.matrices.expressions.dotproduct import DotProduct
from sympy.utilities.pytest import raises

A = Matrix(3, 1, [1, 2, 3])
B = Matrix(3, 1, [1, 3, 5])
C = Matrix(4, 1, [1, 2, 4, 5])
D = Matrix(2, 2, [1, 2, 3, 4])

def test_docproduct():
    """
    Test the DotProduct function with various matrix inputs and operations. The function checks the correctness of the DotProduct for different matrix combinations and orientations. It also raises TypeError for invalid inputs.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If the inputs are not valid for the DotProduct operation.
    
    Example usage:
    >>> test_docproduct()
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
