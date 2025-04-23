import numpy as np
from numpy.testing import assert_array_equal

from xarray.core.nputils import NumpyVIndexAdapter, _is_contiguous


def test_is_contiguous():
    """
    Tests the `_is_contiguous` function.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the list is not contiguous.
    
    Examples:
    >>> test_is_contiguous()
    True
    >>> test_is_contiguous([1, 2, 3])
    True
    >>> test_is_contiguous([1, 3])
    False
    """

    assert _is_contiguous([1])
    assert _is_contiguous([1, 2, 3])
    assert not _is_contiguous([1, 3])


def test_vindex():
    """
    Test the VIndexAdapter functionality for a 3D numpy array.
    
    Parameters:
    None
    
    Returns:
    None
    
    This function tests the VIndexAdapter for a 3D numpy array. It checks the
    correctness of both getitem and setitem operations for various slicing
    combinations. The array is initialized with a range of values reshaped into
    a 3x4x5 tensor. The tests verify that the VIndexAdapter behaves as expected
    for different indexing scenarios, including
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
