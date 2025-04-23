from sympy.tensor.array import (ImmutableDenseNDimArray,
        ImmutableSparseNDimArray, MutableDenseNDimArray, MutableSparseNDimArray)
from sympy.abc import x, y, z


def test_NDim_array_conv():
    """
    Converts between mutable and immutable dense and sparse N-dimensional array representations.
    
    This function takes an N-dimensional array and converts it between its mutable and immutable dense and sparse representations.
    
    Parameters:
    array (MutableDenseNDimArray, MutableSparseNDimArray, ImmutableDenseNDimArray, ImmutableSparseNDimArray): The N-dimensional array to be converted.
    
    Returns:
    (MutableDenseNDimArray, MutableSparseNDimArray, ImmutableDenseNDimArray, ImmutableSparseND
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
