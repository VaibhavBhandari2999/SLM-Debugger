from sympy.tensor.functions import TensorProduct
from sympy.matrices.dense import Matrix
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.tensor.array import Array
from sympy.abc import x, y, z
from sympy.abc import i, j, k, l


A = MatrixSymbol("A", 3, 3)
B = MatrixSymbol("B", 3, 3)
C = MatrixSymbol("C", 3, 3)


def test_TensorProduct_construction():
    """
    Constructs a tensor product of two or more inputs.
    
    This function takes two or more inputs and constructs a tensor product of them. It supports both numeric and symbolic inputs. The function can handle nested tensor products and matrix/array operations.
    
    Parameters:
    *args: Variable length argument list. Can be integers, symbols, matrices, or arrays.
    
    Returns:
    int or TensorProduct: If all inputs are integers, returns the product of those integers. Otherwise, returns a TensorProduct object representing the tensor product
    """

    assert TensorProduct(3, 4) == 12
    assert isinstance(TensorProduct(A, A), TensorProduct)

    expr = TensorProduct(TensorProduct(x, y), z)
    assert expr == x*y*z

    expr = TensorProduct(TensorProduct(A, B), C)
    assert expr == TensorProduct(A, B, C)

    expr = TensorProduct(Matrix.eye(2), Array([[0, -1], [1, 0]]))
    assert expr == Array([
        [
            [[0, -1], [1, 0]],
            [[0, 0], [0, 0]]
        ],
        [
            [[0, 0], [0, 0]],
            [[0, -1], [1, 0]]
        ]
    ])


def test_TensorProduct_shape():
    """
    Test the shape of a TensorProduct expression.
    
    Parameters:
    - expr (TensorProduct): A TensorProduct expression to test.
    
    Returns:
    - tuple: The shape of the TensorProduct expression.
    - int: The rank (number of dimensions) of the TensorProduct expression.
    
    This function checks the shape and rank of a TensorProduct expression with different inputs, including arrays and matrices.
    """


    expr = TensorProduct(3, 4, evaluate=False)
    assert expr.shape == ()
    assert expr.rank() == 0

    expr = TensorProduct(Array([1, 2]), Array([x, y]), evaluate=False)
    assert expr.shape == (2, 2)
    assert expr.rank() == 2
    expr = TensorProduct(expr, expr, evaluate=False)
    assert expr.shape == (2, 2, 2, 2)
    assert expr.rank() == 4

    expr = TensorProduct(Matrix.eye(2), Array([[0, -1], [1, 0]]), evaluate=False)
    assert expr.shape == (2, 2, 2, 2)
    assert expr.rank() == 4


def test_TensorProduct_getitem():
    expr = TensorProduct(A, B)
    assert expr[i, j, k, l] == A[i, j]*B[k, l]
