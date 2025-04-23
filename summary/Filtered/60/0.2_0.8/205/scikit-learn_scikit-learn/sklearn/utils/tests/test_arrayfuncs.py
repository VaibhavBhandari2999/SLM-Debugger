import pytest
import numpy as np

from sklearn.utils._testing import assert_allclose
from sklearn.utils.arrayfuncs import min_pos


def test_min_pos():
    """
    Find the index of the minimum positive value in an array.
    
    This function returns the index of the smallest positive value in the given array. If no positive value is found, it returns -1. The function supports both float and double data types.
    
    Parameters:
    X (numpy.ndarray): Input array of numeric values (float or double).
    
    Returns:
    int: Index of the smallest positive value in the array, or -1 if no positive value is found.
    
    Examples:
    >>> X = np.random
    """

    # Check that min_pos returns a positive value and that it's consistent
    # between float and double
    X = np.random.RandomState(0).randn(100)

    min_double = min_pos(X)
    min_float = min_pos(X.astype(np.float32))

    assert_allclose(min_double, min_float)
    assert min_double >= 0


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_min_pos_no_positive(dtype):
    """
    Test the min_pos function for an array with no positive values.
    
    This function checks that the return value of `min_pos` is the maximum
    representable value of the input data type when all elements in the input
    array are less than or equal to zero. This is a test case to ensure that the
    function correctly handles arrays with no positive values.
    
    Parameters:
    dtype (numpy.dtype): The data type of the input array.
    
    Returns:
    None: This function does not return any value
    """

    # Check that the return value of min_pos is the maximum representable
    # value of the input dtype when all input elements are <= 0 (#19328)
    X = np.full(100, -1.0).astype(dtype, copy=False)

    assert min_pos(X) == np.finfo(dtype).max
