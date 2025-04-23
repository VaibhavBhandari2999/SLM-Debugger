from sklearn.utils.testing import (assert_array_equal, assert_equal,
                                   assert_raises)

from scipy.sparse import bsr_matrix, csc_matrix, csr_matrix

from sklearn.feature_selection import VarianceThreshold

data = [[0, 1, 2, 3, 4],
        [0, 2, 2, 3, 5],
        [1, 1, 2, 4, 0]]


def test_zero_variance():
    """
    Test the VarianceThreshold transformer for zero variance filtering.
    
    Parameters:
    X (array-like or sparse matrix): The input data to fit the transformer on.
    
    This function tests the `VarianceThreshold` transformer with default settings to filter out features with zero variance. It works with both dense and sparse input data. The function verifies that the transformer correctly identifies and removes features with zero variance. It also raises a `ValueError` for cases where the input data does not have enough variability.
    
    The function accepts
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
ape)
