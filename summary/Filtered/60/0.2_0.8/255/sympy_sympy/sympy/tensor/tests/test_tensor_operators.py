from sympy.tensor.toperators import PartialDerivative
from sympy.tensor.tensor import TensorIndexType, tensor_indices, tensorhead
from sympy import symbols, diag
from sympy import Array


L = TensorIndexType("L")
i, j, k = tensor_indices("i j k", L)
i0 = tensor_indices("i0", L)
L_0 = tensor_indices("L_0", L)

A, B, C, D = tensorhead("A B C D", [L], [[1]])

H = tensorhead("H", [L, L], [[1], [1]])


def test_tensor_partial_deriv():
    """
    Test partial derivatives of tensors.
    
    Parameters:
    expr (Expression): The expression involving partial derivatives of tensors.
    
    Returns:
    None: This function does not return any value. It performs assertions to validate the behavior of partial derivatives on tensors.
    
    Key Points:
    - The function tests the behavior of partial derivatives on tensors, including flattening and handling of multiple indices.
    - It checks the expression and variables involved in the partial derivatives.
    - The function ensures that the indices are correctly handled and that the expressions are simplified
    """

    # Test flatten:
    expr = PartialDerivative(PartialDerivative(A(i), A(j)), A(-i))
    assert expr.expr == A(L_0)
    assert expr.variables == (A(j), A(-L_0))

    expr1 = PartialDerivative(A(i), A(j))
    assert expr1.expr == A(i)
    assert expr1.variables == (A(j),)

    expr2 = A(i)*PartialDerivative(H(k, -i), A(j))
    assert expr2.get_indices() == [L_0, k, -L_0, j]

    expr3 = A(i)*PartialDerivative(B(k)*C(-i) + 3*H(k, -i), A(j))
    assert expr3.get_indices() == [L_0, k, -L_0, j]

    expr4 = (A(i) + B(i))*PartialDerivative(C(-j), D(j))
    assert expr4.get_indices() == [i, -L_0, L_0]

    expr5 = (A(i) + B(i))*PartialDerivative(C(-i), D(j))
    assert expr5.get_indices() == [L_0, -L_0, j]


def test_replace_arrays_partial_derivative():
    """
    Test the replacement of arrays in partial derivatives.
    
    This function tests the replacement of arrays in partial derivatives with specified mappings and conditions.
    
    Parameters:
    expr (PartialDerivative): The partial derivative expression to be tested.
    replacements (dict): A dictionary mapping symbolic arrays to actual arrays.
    indices (list): A list of symbolic indices to be replaced.
    
    Returns:
    The result of the replacement and evaluation of the partial derivative expression.
    """

    x, y, z, t = symbols("x y z t")

    expr = PartialDerivative(A(i), A(j))
    assert expr.replace_with_arrays({A(i): [x, y]}, [i, j]) == Array([[1, 0], [0, 1]])

    expr = PartialDerivative(A(i), A(-i))
    assert expr.replace_with_arrays({A(i): [x, y], L: diag(1, 1)}, []) == 2
    assert expr.replace_with_arrays({A(i): [x, y], L: diag(1, -1)}, []) == 0

    expr = PartialDerivative(A(-i), A(i))
    assert expr.replace_with_arrays({A(i): [x, y], L: diag(1, 1)}, []) == 2
    assert expr.replace_with_arrays({A(i): [x, y], L: diag(1, -1)}, []) == 0
