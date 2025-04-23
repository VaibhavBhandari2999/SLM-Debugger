import numpy as np
from numpy.testing import assert_array_equal

from xarray.core.nputils import NumpyVIndexAdapter, _is_contiguous, rolling_window


def test_is_contiguous():
    assert _is_contiguous([1])
    assert _is_contiguous([1, 2, 3])
    assert not _is_contiguous([1, 3])


def test_vindex():
    """
    Test VIndex Adapter.
    
    This function tests the VIndexAdapter, a class designed to adapt a numpy array
    for efficient slicing and indexing operations. The VIndexAdapter is expected
    to provide similar functionality to numpy's advanced indexing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Operations Tested:
    - Getitem: Verify that the VIndexAdapter correctly handles various slicing
    and indexing operations.
    - Setitem: Verify that the VIndexAdapter correctly handles assignment
    operations for different
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


def test_rolling():
    x = np.array([1, 2, 3, 4], dtype=float)

    actual = rolling_window(x, axis=-1, window=3, center=True, fill_value=np.nan)
    expected = np.array(
        [[np.nan, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, np.nan]], dtype=float
    )
    assert_array_equal(actual, expected)

    actual = rolling_window(x, axis=-1, window=3, center=False, fill_value=0.0)
    expected = np.array([[0, 0, 1], [0, 1, 2], [1, 2, 3], [2, 3, 4]], dtype=float)
    assert_array_equal(actual, expected)

    x = np.stack([x, x * 1.1])
    actual = rolling_window(x, axis=-1, window=3, center=False, fill_value=0.0)
    expected = np.stack([expected, expected * 1.1], axis=0)
    assert_array_equal(actual, expected)
