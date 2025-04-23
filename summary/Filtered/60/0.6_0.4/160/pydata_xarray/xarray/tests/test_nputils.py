import numpy as np
from numpy.testing import assert_array_equal

from xarray.core.nputils import NumpyVIndexAdapter, _is_contiguous


def test_is_contiguous():
    assert _is_contiguous([1])
    assert _is_contiguous([1, 2, 3])
    assert not _is_contiguous([1, 3])


def test_vindex():
    """
    Tests the VIndexAdapter functionality for a 3D numpy array.
    
    This function verifies the getitem and setitem operations of the VIndexAdapter
    for a 3D numpy array. The VIndexAdapter is used to adapt a 3D numpy array for
    vectorized indexing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations Tested:
    - getitem with single and multiple indices
    - getitem with slicing
    - setitem with single and multiple indices
    """

    x = np.arange(3 * 4 * 5).reshape((3, 4, 5))
    vindex = NumpyVIndexAdapter(x)

    # getitem
    assert_array_equal(vindex[0], x[0])
    assert_array_equal(vindex[[1, 2], [1, 2]], x[[1, 2], [1, 2]])
    assert vindex[[0, 1], [0, 1], :].shape == (2, 5)
    assert vindex[[0, 1], :, [0, 1]].shape == (2, 4)
    assert vindex[:, [0, 1], [0, 1]].shape == (2, 3)

    # setitem
    vindex[:] = 0
    assert_array_equal(x, np.zeros_like(x))
    # assignment should not raise
    vindex[[0, 1], [0, 1], :] = vindex[[0, 1], [0, 1], :]
    vindex[[0, 1], :, [0, 1]] = vindex[[0, 1], :, [0, 1]]
    vindex[:, [0, 1], [0, 1]] = vindex[:, [0, 1], [0, 1]]
