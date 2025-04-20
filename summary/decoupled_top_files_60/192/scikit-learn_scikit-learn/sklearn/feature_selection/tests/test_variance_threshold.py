from sklearn.utils.testing import (assert_array_equal, assert_equal,
                                   assert_raises)

from scipy.sparse import bsr_matrix, csc_matrix, csr_matrix

from sklearn.feature_selection import VarianceThreshold

data = [[0, 1, 2, 3, 4],
        [0, 2, 2, 3, 5],
        [1, 1, 2, 4, 0]]


def test_zero_variance():
    """
    Tests the VarianceThreshold transformer to filter out features with zero variance.
    
    This function verifies that the VarianceThreshold transformer correctly identifies and removes features with zero variance from the input dataset. It supports various matrix formats including dense and sparse matrices. The function also checks for scenarios where the transformer raises a ValueError due to inappropriate input data.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the input data does not meet the requirements for the VarianceThreshold transformer.
    
    Test Cases:
    """

    # Test VarianceThreshold with default setting, zero variance.

    for X in [data, csr_matrix(data), csc_matrix(data), bsr_matrix(data)]:
        sel = VarianceThreshold().fit(X)
        assert_array_equal([0, 1, 3, 4], sel.get_support(indices=True))

    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1, 2, 3]])
    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1], [0, 1]])


def test_variance_threshold():
    # Test VarianceThreshold with custom variance.
    for X in [data, csr_matrix(data)]:
        X = VarianceThreshold(threshold=.4).fit_transform(X)
        assert_equal((len(data), 1), X.shape)
