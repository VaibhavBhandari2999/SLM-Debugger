from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Converts between mutable and immutable dense and sparse N-dimensional array types.
    
    This function allows for the conversion of N-dimensional arrays between their mutable and immutable dense and sparse variants. It supports four types of arrays:
    - MutableDenseNDimArray: A mutable dense N-dimensional array.
    - MutableSparseNDimArray: A mutable sparse N-dimensional array.
    - ImmutableDenseNDimArray: An immutable dense N-dimensional array.
    - ImmutableSparseNDimArray: An immutable sparse N-dimensional array.
    
    Parameters
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
