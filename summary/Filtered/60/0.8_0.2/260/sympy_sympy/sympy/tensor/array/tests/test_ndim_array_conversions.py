from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Convert between mutable and immutable N-dimensional array types.
    
    This function allows conversion between mutable and immutable N-dimensional array types. It supports both dense and sparse array types.
    
    Parameters:
    MD (MutableDenseNDimArray): A mutable dense N-dimensional array.
    MS (MutableSparseNDimArray): A mutable sparse N-dimensional array.
    ID (ImmutableDenseNDimArray): An immutable dense N-dimensional array.
    IS (ImmutableSparseNDimArray): An immutable sparse N-dimensional array.
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
