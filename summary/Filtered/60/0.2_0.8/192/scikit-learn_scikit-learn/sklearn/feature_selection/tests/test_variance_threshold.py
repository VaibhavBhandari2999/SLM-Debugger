from sklearn.utils.testing import (assert_array_equal, assert_equal,
                                   assert_raises)

from scipy.sparse import bsr_matrix, csc_matrix, csr_matrix

from sklearn.feature_selection import VarianceThreshold

data = [[0, 1, 2, 3, 4],
        [0, 2, 2, 3, 5],
        [1, 1, 2, 4, 0]]


def test_zero_variance():
    """
    Test VarianceThreshold with default settings, zero variance.
    
    This function tests the `VarianceThreshold` class from scikit-learn with default parameters to filter out features with zero variance. It checks the output of the `get_support` method to ensure that the correct features are selected. The function also raises a `ValueError` for invalid input cases.
    
    Parameters:
    - X: array-like or sparse matrix, shape (n_samples, n_features)
    The input data to fit the `Variance
    """

    # Test VarianceThreshold with default setting, zero variance.

    for X in [data, csr_matrix(data), csc_matrix(data), bsr_matrix(data)]:
        sel = VarianceThreshold().fit(X)
        assert_array_equal([0, 1, 3, 4], sel.get_support(indices=True))

    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1, 2, 3]])
    assert_raises(ValueError, VarianceThreshold().fit, [[0, 1], [0, 1]])


def test_variance_threshold():
    """
    Test the VarianceThreshold function.
    
    Parameters:
    data (array-like or sparse matrix): The input data to be filtered based on variance.
    
    Returns:
    array-like or sparse matrix: The transformed data with low variance features removed.
    
    This function applies the VarianceThreshold transformer to the input data, filtering out features with a variance lower than the specified threshold (.4 in this case). The transformed data is returned with the low variance features removed.
    """

    # Test VarianceThreshold with custom variance.
    for X in [data, csr_matrix(data)]:
        X = VarianceThreshold(threshold=.4).fit_transform(X)
        assert_equal((len(data), 1), X.shape)
