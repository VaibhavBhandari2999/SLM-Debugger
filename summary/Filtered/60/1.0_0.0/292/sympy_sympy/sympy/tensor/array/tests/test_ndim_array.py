from sympy.testing.pytest import raises
from sympy.functions.elementary.trigonometric import sin, cos
from sympy.matrices.dense import Matrix
from sympy.simplify import simplify
from sympy.tensor.array import Array
from sympy.tensor.array.dense_ndim_array import (
    ImmutableDenseNDimArray, MutableDenseNDimArray)
from sympy.tensor.array.sparse_ndim_array import (
    ImmutableSparseNDimArray, MutableSparseNDimArray)

from sympy.abc import x, y

array_types = [
    ImmutableDenseNDimArray,
    ImmutableSparseNDimArray,
    MutableDenseNDimArray,
    MutableSparseNDimArray
]


def test_array_negative_indices():
    for ArrayType in array_types:
        test_array = ArrayType([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
        assert test_array[:, -1] == Array([5, 10])
        assert test_array[:, -2] == Array([4, 9])
        assert test_array[:, -3] == Array([3, 8])
        assert test_array[:, -4] == Array([2, 7])
        assert test_array[:, -5] == Array([1, 6])
        assert test_array[:, 0] == Array([1, 6])
        assert test_array[:, 1] == Array([2, 7])
        assert test_array[:, 2] == Array([3, 8])
        assert test_array[:, 3] == Array([4, 9])
        assert test_array[:, 4] == Array([5, 10])

        raises(ValueError, lambda: test_array[:, -6])
        raises(ValueError, lambda: test_array[-3, :])

        assert test_array[-1, -1] == 10


def test_issue_18361():
    """
    Simplify the given symbolic expressions.
    
    This function simplifies the provided symbolic expressions and returns the simplified forms.
    
    Parameters:
    A (Array): An array of symbolic expressions.
    B (Array): Another array of symbolic expressions.
    C (Array): A third array of symbolic expressions.
    
    Returns:
    Array: An array of simplified symbolic expressions.
    
    Example:
    >>> A = Array([sin(2 * x) - 2 * sin(x) * cos(x)])
    >>> B = Array([
    """

    A = Array([sin(2 * x) - 2 * sin(x) * cos(x)])
    B = Array([sin(x)**2 + cos(x)**2, 0])
    C = Array([(x + x**2)/(x*sin(y)**2 + x*cos(y)**2), 2*sin(x)*cos(x)])
    assert simplify(A) == Array([0])
    assert simplify(B) == Array([1, 0])
    assert simplify(C) == Array([x + 1, sin(2*x)])

def test_issue_20222():
    """
    Test for issue 20222.
    
    This function checks the behavior of subtracting a Matrix from an Array.
    
    Parameters:
    A (Array): An array with shape (2, 2).
    B (Matrix): A matrix with shape (2, 2).
    
    Raises:
    TypeError: If the subtraction operation between an Array and a Matrix is not supported.
    """

    A = Array([[1, 2], [3, 4]])
    B = Matrix([[1,2],[3,4]])
    raises(TypeError, lambda: A - B)
