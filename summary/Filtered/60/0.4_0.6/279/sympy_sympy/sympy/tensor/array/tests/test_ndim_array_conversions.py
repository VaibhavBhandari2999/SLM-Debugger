from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Converts between mutable and immutable dense and sparse N-dimensional array types.
    
    This function allows conversion between different types of N-dimensional arrays:
    - From mutable to immutable dense array
    - From mutable to mutable dense array
    - From mutable to immutable sparse array
    - From mutable to mutable sparse array
    - From immutable to immutable dense array
    - From immutable to mutable dense array
    - From immutable to immutable sparse array
    - From immutable to mutable sparse array
    
    Parameters:
    MD (MutableDenseNDim
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
