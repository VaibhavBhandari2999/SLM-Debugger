from sympy.matrices import Matrix
from sympy.matrices.expressions.dotproduct import DotProduct
from sympy.utilities.pytest import raises

A = Matrix(3, 1, [1, 2, 3])
B = Matrix(3, 1, [1, 3, 5])
C = Matrix(4, 1, [1, 2, 4, 5])
D = Matrix(2, 2, [1, 2, 3, 4])

def test_docproduct():
    """
    Test the DotProduct function with various matrix operations and inputs. The function checks the correctness of the DotProduct for different matrix combinations and raises TypeError for invalid inputs.
    
    Parameters:
    A, B (Matrix): Input matrices for the DotProduct.
    D, C (Matrix): Additional matrices for testing invalid inputs.
    
    Returns:
    None
    
    Raises:
    TypeError: If the inputs are not valid matrices or if the DotProduct cannot be computed due to incompatible dimensions.
    
    Examples:
    assert DotProduct(A, B).doit()
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
