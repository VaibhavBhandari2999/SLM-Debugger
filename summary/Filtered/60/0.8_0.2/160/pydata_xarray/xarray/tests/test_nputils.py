import numpy as np
from numpy.testing import assert_array_equal

from xarray.core.nputils import NumpyVIndexAdapter, _is_contiguous


def test_is_contiguous():
    assert _is_contiguous([1])
    assert _is_contiguous([1, 2, 3])
    assert not _is_contiguous([1, 3])


def test_vindex():
    """
    Test VIndex Adapter.
    
    This function tests the VIndexAdapter, a class that provides vectorized indexing
    for a NumPy array. The VIndexAdapter is initialized with a 3D NumPy array and
    provides methods to perform getitem and setitem operations on the array using
    vectorized indices.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations:
    - getitem: Access elements of the array using vectorized indices.
    - setitem: Assign values to elements
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
