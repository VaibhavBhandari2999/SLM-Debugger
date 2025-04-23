from sympy.tensor.tensor import (Tensor, TensorIndexType, TensorSymmetry,
        tensor_indices, TensorHead, TensorElement)
from sympy.tensor import Array
from sympy.core.symbol import Symbol


def test_tensor_element():
    """
    Tests the creation and manipulation of TensorElement objects.
    
    This function creates a tensor element from a tensor head and verifies the creation and replacement of TensorElement objects. It also checks the free and dummy indices of the TensorElement.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - Creates a tensor element from a tensor head.
    - Verifies the creation of TensorElement objects with and without specified indices.
    - Checks the free and dummy indices of the TensorElement.
    - Replaces the tensor element
    """

    L = TensorIndexType("L")
    i, j, k, l, m, n = tensor_indices("i j k l m n", L)

    A = TensorHead("A", [L, L], TensorSymmetry.no_symmetry(2))

    a = A(i, j)

    assert isinstance(TensorElement(a, {}), Tensor)
    assert isinstance(TensorElement(a, {k: 1}), Tensor)

    te1 = TensorElement(a, {Symbol("i"): 1})
    assert te1.free == [(j, 0)]
    assert te1.get_free_indices() == [j]
    assert te1.dum == []

    te2 = TensorElement(a, {i: 1})
    assert te2.free == [(j, 0)]
    assert te2.get_free_indices() == [j]
    assert te2.dum == []

    assert te1 == te2

    array = Array([[1, 2], [3, 4]])
    assert te1.replace_with_arrays({A(i, j): array}, [j]) == array[1, :]
