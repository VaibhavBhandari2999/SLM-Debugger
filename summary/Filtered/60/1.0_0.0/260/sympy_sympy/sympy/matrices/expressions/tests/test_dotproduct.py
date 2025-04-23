from sympy.matrices import Matrix
from sympy.matrices.expressions.dotproduct import DotProduct
from sympy.utilities.pytest import raises

A = Matrix(3, 1, [1, 2, 3])
B = Matrix(3, 1, [1, 3, 5])
C = Matrix(4, 1, [1, 2, 4, 5])
D = Matrix(2, 2, [1, 2, 3, 4])

def test_docproduct():
    """
    Test the DotProduct function with various matrix inputs and operations.
    
    Key Parameters:
    - A, B: Matrix inputs for the DotProduct function.
    - D: A matrix that is not compatible for DotProduct with A or B.
    
    Input:
    - A, B: Matrices for which the DotProduct is calculated.
    - D: A matrix that is not compatible for DotProduct with A or B.
    
    Output:
    - The result of the DotProduct for valid matrix inputs.
    - Raises TypeError for invalid inputs or
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
