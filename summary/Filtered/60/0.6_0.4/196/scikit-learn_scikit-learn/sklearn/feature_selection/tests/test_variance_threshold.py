from sklearn.utils.testing import (assert_array_equal, assert_equal,
                                   assert_raises)

from scipy.sparse import bsr_matrix, csc_matrix, csr_matrix

from sklearn.feature_selection import VarianceThreshold

data = [[0, 1, 2, 3, 4],
        [0, 2, 2, 3, 5],
        [1, 1, 2, 4, 0]]


def test_zero_variance():
    """
    Test VarianceThreshold with default setting, zero variance.
    
    This function tests the `VarianceThreshold` class from scikit-learn with default settings to filter out features with zero variance. It checks the function's behavior on different types of input data (dense and sparse matrices) and raises a `ValueError` for invalid input cases.
    
    Parameters:
    X : array-like or sparse matrix
    Input data to test the `VarianceThreshold` filter on.
    
    Returns:
    None: This function does
    """

    # Test VarianceThreshold with default setting, zero variance.

    for X in [data, csr_matrix(data), csc_matrix(data), bsr_matrix(data)]:
        sel = VarianceThreshold().fit(X)
        assert_array_equal([0, 1, 3, 4], sel.get_support(indices=True))

    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1, 2, 3]])
    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1], [0, 1]])


def test_variance_threshold():
    """
    Test VarianceThreshold with custom variance threshold.
    
    Parameters:
    X (array-like or sparse matrix): The input data.
    
    Returns:
    array-like or sparse matrix: The transformed data with features that have zero variance removed.
    """

    # Test VarianceThreshold with custom variance.
    for X in [data, csr_matrix(data)]:
        X = VarianceThreshold(threshold=.4).fit_transform(X)
        assert_equal((len(data), 1), X.shape)
