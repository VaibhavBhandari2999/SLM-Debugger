from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Converts between mutable and immutable N-dimensional arrays.
    
    This function can convert a mutable N-dimensional array to an immutable one and vice versa. It supports both dense and sparse array types.
    
    Parameters:
    MD (MutableDenseNDimArray, MutableSparseNDimArray): A mutable N-dimensional array.
    MS (MutableDenseNDimArray, MutableSparseNDimArray): Another mutable N-dimensional array.
    ID (ImmutableDenseNDimArray, ImmutableSparseNDimArray): An immutable
    """

    MD = MutableDenseNDimArray([x, y, z])
    MS = MutableSparseNDimArray([x, y, z])
    ID = ImmutableDenseNDimArray([x, y, z])
    IS = ImmutableSparseNDimArray([x, y, z])

    assert MD.as_immutable() == ID
    assert MD.as_mutable() == MD

    assert MS.as_immutable() == IS
    assert MS.as_mutable() == MS

    assert ID.as_immutable() == ID
    assert ID.as_mutable() == MD

    assert IS.as_immutable() == IS
    assert IS.as_mutable() == MS
