import pytest
import numpy as np

from sklearn.utils._testing import assert_allclose
from sklearn.utils.arrayfuncs import min_pos


def test_min_pos():
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
    
    This function verifies that for an array of the specified data type (`dtype`),
    where all elements are less than or equal to zero, the `min_pos` function returns
    the maximum representable value of that data type. This is a test case to ensure
    correct behavior of the `min_pos` function in edge cases.
    
    Parameters:
    dtype (str or numpy.dtype): The data type of the input array.
    
    Returns:
    """

    # Check that the return value of min_pos is the maximum representable
    # value of the input dtype when all input elements are <= 0 (#19328)
    X = np.full(100, -1.0).astype(dtype, copy=False)

    assert min_pos(X) == np.finfo(dtype).max
(dtype).max
