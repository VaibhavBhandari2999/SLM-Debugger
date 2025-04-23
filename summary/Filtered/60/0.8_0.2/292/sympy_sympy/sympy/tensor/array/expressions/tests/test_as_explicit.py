from sympy.core.symbol import Symbol
from sympy.matrices.expressions.matexpr import MatrixSymbol
from sympy.tensor.array.arrayop import (permutedims, tensorcontraction, tensordiagonal, tensorproduct)
from sympy.tensor.array.dense_ndim_array import ImmutableDenseNDimArray
from sympy.tensor.array.expressions.array_expressions import ZeroArray, OneArray, ArraySymbol, \
    ArrayTensorProduct, PermuteDims, ArrayDiagonal, ArrayContraction, ArrayAdd
from sympy.testing.pytest import raises


def test_array_as_explicit_call():
    """
    test_array_as_explicit_call
    
    This function tests the as_explicit method for various array and tensor expressions. It verifies that the method correctly converts symbolic array and tensor expressions into their explicit form.
    
    Parameters:
    - No explicit parameters are required for this function.
    
    Returns:
    - None
    
    Raises:
    - ValueError: If the input array dimensions are symbolic or not fully specified.
    
    Key Expressions:
    - ZeroArray(3, 2, 4): Creates a 3x2x4 zero array and
    """


    assert ZeroArray(3, 2, 4).as_explicit() == ImmutableDenseNDimArray.zeros(3, 2, 4)
    assert OneArray(3, 2, 4).as_explicit() == ImmutableDenseNDimArray([1 for i in range(3*2*4)]).reshape(3, 2, 4)

    k = Symbol("k")
    X = ArraySymbol("X", (k, 3, 2))
    raises(ValueError, lambda: X.as_explicit())
    raises(ValueError, lambda: ZeroArray(k, 2, 3).as_explicit())
    raises(ValueError, lambda: OneArray(2, k, 2).as_explicit())

    A = ArraySymbol("A", (3, 3))
    B = ArraySymbol("B", (3, 3))

    texpr = tensorproduct(A, B)
    assert isinstance(texpr, ArrayTensorProduct)
    assert texpr.as_explicit() == tensorproduct(A.as_explicit(), B.as_explicit())

    texpr = tensorcontraction(A, (0, 1))
    assert isinstance(texpr, ArrayContraction)
    assert texpr.as_explicit() == A[0, 0] + A[1, 1] + A[2, 2]

    texpr = tensordiagonal(A, (0, 1))
    assert isinstance(texpr, ArrayDiagonal)
    assert texpr.as_explicit() == ImmutableDenseNDimArray([A[0, 0], A[1, 1], A[2, 2]])

    texpr = permutedims(A, [1, 0])
    assert isinstance(texpr, PermuteDims)
    assert texpr.as_explicit() == permutedims(A.as_explicit(), [1, 0])


def test_array_as_explicit_matrix_symbol():

    A = MatrixSymbol("A", 3, 3)
    B = MatrixSymbol("B", 3, 3)

    texpr = tensorproduct(A, B)
    assert isinstance(texpr, ArrayTensorProduct)
    assert texpr.as_explicit() == tensorproduct(A.as_explicit(), B.as_explicit())

    texpr = tensorcontraction(A, (0, 1))
    assert isinstance(texpr, ArrayContraction)
    assert texpr.as_explicit() == A[0, 0] + A[1, 1] + A[2, 2]

    texpr = tensordiagonal(A, (0, 1))
    assert isinstance(texpr, ArrayDiagonal)
    assert texpr.as_explicit() == ImmutableDenseNDimArray([A[0, 0], A[1, 1], A[2, 2]])

    texpr = permutedims(A, [1, 0])
    assert isinstance(texpr, PermuteDims)
    assert texpr.as_explicit() == permutedims(A.as_explicit(), [1, 0])

    expr = ArrayAdd(ArrayTensorProduct(A, B), ArrayTensorProduct(B, A))
    assert expr.as_explicit() == expr.args[0].as_explicit() + expr.args[1].as_explicit()
