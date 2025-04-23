from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Converts between mutable and immutable dense and sparse N-dimensional array types.
    
    This function takes an N-dimensional array in any of the four possible types (MutableDenseNDimArray, MutableSparseNDimArray, ImmutableDenseNDimArray, ImmutableSparseNDimArray) and converts it to its corresponding type. It can also convert between mutable and immutable types.
    
    Parameters:
    array (MutableDenseNDimArray, MutableSparseNDimArray, ImmutableDenseNDimArray, ImmutableSparse
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
