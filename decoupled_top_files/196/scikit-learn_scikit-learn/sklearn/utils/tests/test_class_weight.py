import numpy as np
import pytest

from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_blobs

from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils.class_weight import compute_sample_weight

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_raise_message
from sklearn.utils.testing import assert_equal


def test_compute_class_weight():
    """
    Compute class weights for balanced dataset.
    
    This function calculates the class weights for a given set of target values
    using the 'balanced' method. It takes an array of target values `y` and
    returns an array of class weights.
    
    Parameters:
    -----------
    y : numpy.ndarray
    An array of target values.
    
    Returns:
    --------
    class_weights : numpy.ndarray
    An array of computed class weights.
    
    Example:
    --------
    >>> y = np.array
    """

    # Test (and demo) compute_class_weight.
    y = np.asarray([2, 2, 2, 3, 3, 4])
    classes = np.unique(y)

    cw = compute_class_weight("balanced", classes, y)
    # total effect of samples is preserved
    class_counts = np.bincount(y)[2:]
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert cw[0] < cw[1] < cw[2]


def test_compute_class_weight_not_present():
    """
    Raise errors for invalid inputs in `compute_class_weight` function.
    
    This function checks for the presence of all class labels in the input
    array `y` and raises appropriate errors if any label is missing or if
    there are additional labels not present in the `classes` array.
    
    Parameters:
    -----------
    classes : numpy.ndarray
    Array containing the unique class labels.
    
    y : numpy.ndarray
    Input array containing the target labels.
    
    Returns:
    --------
    None
    """

    # Raise error when y does not contain all class labels
    classes = np.arange(4)
    y = np.asarray([0, 0, 0, 1, 1, 2])
    assert_raises(ValueError, compute_class_weight, "balanced", classes, y)
    # Fix exception in error message formatting when missing label is a string
    # https://github.com/scikit-learn/scikit-learn/issues/8312
    assert_raise_message(ValueError,
                         'Class label label_not_present not present',
                         compute_class_weight,
                         {'label_not_present': 1.}, classes, y)
    # Raise error when y has items not in classes
    classes = np.arange(2)
    assert_raises(ValueError, compute_class_weight, "balanced", classes, y)
    assert_raises(ValueError, compute_class_weight, {0: 1., 1: 2.}, classes, y)


def test_compute_class_weight_dict():
    """
    Computes class weights based on the specified dictionary of class weights.
    
    Parameters:
    -----------
    class_weights : dict
    A dictionary specifying the class weights for each class label.
    classes : array-like
    An array containing the unique class labels present in the dataset.
    y : array-like
    The target variable containing the class labels for each sample.
    
    Returns:
    --------
    cw : numpy.ndarray
    An array containing the computed class weights for each class label.
    
    Raises
    """

    classes = np.arange(3)
    class_weights = {0: 1.0, 1: 2.0, 2: 3.0}
    y = np.asarray([0, 0, 1, 2])
    cw = compute_class_weight(class_weights, classes, y)

    # When the user specifies class weights, compute_class_weights should just
    # return them.
    assert_array_almost_equal(np.asarray([1.0, 2.0, 3.0]), cw)

    # When a class weight is specified that isn't in classes, a ValueError
    # should get raised
    msg = 'Class label 4 not present.'
    class_weights = {0: 1.0, 1: 2.0, 2: 3.0, 4: 1.5}
    assert_raise_message(ValueError, msg, compute_class_weight, class_weights,
                         classes, y)
    msg = 'Class label -1 not present.'
    class_weights = {-1: 5.0, 0: 1.0, 1: 2.0, 2: 3.0}
    assert_raise_message(ValueError, msg, compute_class_weight, class_weights,
                         classes, y)


@pytest.mark.filterwarnings('ignore: Default solver will be changed')  # 0.22
@pytest.mark.filterwarnings('ignore: Default multi_class will')  # 0.22
def test_compute_class_weight_invariance():
    """
    Test the invariance of model results when using class_weight="balanced" in Logistic Regression.
    
    This function verifies that the Logistic Regression model trained with class_weight="balanced" produces consistent results regardless of class imbalance, given an equal number of samples for each class. The function creates three datasets with different class imbalances but the same total number of samples, and trains a Logistic Regression model on each. The models' coefficients are then compared to ensure they are nearly identical.
    
    Parameters:
    None
    """

    # Test that results with class_weight="balanced" is invariant wrt
    # class imbalance if the number of samples is identical.
    # The test uses a balanced two class dataset with 100 datapoints.
    # It creates three versions, one where class 1 is duplicated
    # resulting in 150 points of class 1 and 50 of class 0,
    # one where there are 50 points in class 1 and 150 in class 0,
    # and one where there are 100 points of each class (this one is balanced
    # again).
    # With balancing class weights, all three should give the same model.
    X, y = make_blobs(centers=2, random_state=0)
    # create dataset where class 1 is duplicated twice
    X_1 = np.vstack([X] + [X[y == 1]] * 2)
    y_1 = np.hstack([y] + [y[y == 1]] * 2)
    # create dataset where class 0 is duplicated twice
    X_0 = np.vstack([X] + [X[y == 0]] * 2)
    y_0 = np.hstack([y] + [y[y == 0]] * 2)
    # duplicate everything
    X_ = np.vstack([X] * 2)
    y_ = np.hstack([y] * 2)
    # results should be identical
    logreg1 = LogisticRegression(class_weight="balanced").fit(X_1, y_1)
    logreg0 = LogisticRegression(class_weight="balanced").fit(X_0, y_0)
    logreg = LogisticRegression(class_weight="balanced").fit(X_, y_)
    assert_array_almost_equal(logreg1.coef_, logreg0.coef_)
    assert_array_almost_equal(logreg.coef_, logreg0.coef_)


def test_compute_class_weight_balanced_negative():
    """
    Compute class weights for balanced class distribution.
    
    This function calculates the class weights for balancing the class distribution
    based on the given labels. It supports both balanced and unbalanced class labels.
    
    Parameters:
    -----------
    classes : numpy.ndarray
    Array of unique class labels.
    y : numpy.ndarray
    Array of target labels.
    
    Returns:
    --------
    class_weights : numpy.ndarray
    Array of computed class weights.
    
    Examples:
    ---------
    >>> classes = np.array
    """

    # Test compute_class_weight when labels are negative
    # Test with balanced class labels.
    classes = np.array([-2, -1, 0])
    y = np.asarray([-1, -1, 0, 0, -2, -2])

    cw = compute_class_weight("balanced", classes, y)
    assert_equal(len(cw), len(classes))
    assert_array_almost_equal(cw, np.array([1., 1., 1.]))

    # Test with unbalanced class labels.
    y = np.asarray([-1, 0, 0, -2, -2, -2])

    cw = compute_class_weight("balanced", classes, y)
    assert_equal(len(cw), len(classes))
    class_counts = np.bincount(y + 2)
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert_array_almost_equal(cw, [2. / 3, 2., 1.])


def test_compute_class_weight_balanced_unordered():
    """
    Compute balanced class weights for an unordered set of classes.
    
    This function calculates the class weights using the 'balanced' strategy
    for an unordered array of classes and corresponding labels. It computes
    the weights such that the sum of the product of weights and class counts
    equals the total number of samples.
    
    Parameters:
    -----------
    classes : numpy.ndarray
    An array containing the unordered classes present in the dataset.
    y : numpy.ndarray
    The target labels corresponding to each
    """

    # Test compute_class_weight when classes are unordered
    classes = np.array([1, 0, 3])
    y = np.asarray([1, 0, 0, 3, 3, 3])

    cw = compute_class_weight("balanced", classes, y)
    class_counts = np.bincount(y)[classes]
    assert_almost_equal(np.dot(cw, class_counts), y.shape[0])
    assert_array_almost_equal(cw, [2., 1., 2. / 3])


def test_compute_class_weight_default():
    """
    Compute class weights for imbalanced datasets.
    
    This function calculates the class weights that can be used to balance
    the dataset by adjusting the importance of each class during training.
    
    Parameters:
    -----------
    class_weight : dict or 'balanced', optional
    - If `None` (default), all classes are treated equally.
    - If a dictionary is provided, it should map each class to its
    corresponding weight.
    - If 'balanced', the class weights will be automatically computed
    """

    # Test for the case where no weight is given for a present class.
    # Current behaviour is to assign the unweighted classes a weight of 1.
    y = np.asarray([2, 2, 2, 3, 3, 4])
    classes = np.unique(y)
    classes_len = len(classes)

    # Test for non specified weights
    cw = compute_class_weight(None, classes, y)
    assert_equal(len(cw), classes_len)
    assert_array_almost_equal(cw, np.ones(3))

    # Tests for partly specified weights
    cw = compute_class_weight({2: 1.5}, classes, y)
    assert_equal(len(cw), classes_len)
    assert_array_almost_equal(cw, [1.5, 1., 1.])

    cw = compute_class_weight({2: 1.5, 4: 0.5}, classes, y)
    assert_equal(len(cw), classes_len)
    assert_array_almost_equal(cw, [1.5, 1., 0.5])


def test_compute_sample_weight():
    """
    Compute sample weights based on class frequencies.
    
    This function calculates the sample weights for each instance in the dataset
    based on the class distribution. It supports various methods such as
    balancing classes, using custom weights, and handling multi-output scenarios.
    
    Parameters:
    -----------
    method : str or None
    The method to compute the sample weights. Options include 'balanced' for
    balancing class frequencies, or None for no weighting.
    
    y : array-like
    The target values
    """

    # Test (and demo) compute_sample_weight.
    # Test with balanced classes
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with user-defined weights
    sample_weight = compute_sample_weight({1: 2, 2: 1}, y)
    assert_array_almost_equal(sample_weight, [2., 2., 2., 1., 1., 1.])

    # Test with column vector of balanced classes
    y = np.asarray([[1], [1], [1], [2], [2], [2]])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with unbalanced classes
    y = np.asarray([1, 1, 1, 2, 2, 2, 3])
    sample_weight = compute_sample_weight("balanced", y)
    expected_balanced = np.array([0.7777, 0.7777, 0.7777, 0.7777, 0.7777,
                                  0.7777, 2.3333])
    assert_array_almost_equal(sample_weight, expected_balanced, decimal=4)

    # Test with `None` weights
    sample_weight = compute_sample_weight(None, y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 1.])

    # Test with multi-output of balanced classes
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with multi-output with user-defined weights
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = compute_sample_weight([{1: 2, 2: 1}, {0: 1, 1: 2}], y)
    assert_array_almost_equal(sample_weight, [2., 2., 2., 2., 2., 2.])

    # Test with multi-output of unbalanced classes
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1], [3, -1]])
    sample_weight = compute_sample_weight("balanced", y)
    assert_array_almost_equal(sample_weight, expected_balanced ** 2, decimal=3)


def test_compute_sample_weight_with_subsample():
    """
    Compute sample weights based on the 'balanced' strategy.
    
    This function calculates sample weights for a given set of target values
    (y) using the 'balanced' strategy. The function supports both single-output
    and multi-output scenarios. It can handle cases where some classes are
    missing in the subsample or when using bootstrapped subsamples.
    
    Parameters:
    -----------
    method : str
    The weighting strategy to use ('balanced').
    y : array-like
    """

    # Test compute_sample_weight with subsamples specified.
    # Test with balanced classes and all samples present
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with column vector of balanced classes and all samples present
    y = np.asarray([[1], [1], [1], [2], [2], [2]])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1.])

    # Test with a subsample
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = compute_sample_weight("balanced", y, range(4))
    assert_array_almost_equal(sample_weight, [2. / 3, 2. / 3,
                                              2. / 3, 2., 2., 2.])

    # Test with a bootstrap subsample
    y = np.asarray([1, 1, 1, 2, 2, 2])
    sample_weight = compute_sample_weight("balanced", y, [0, 1, 1, 2, 2, 3])
    expected_balanced = np.asarray([0.6, 0.6, 0.6, 3., 3., 3.])
    assert_array_almost_equal(sample_weight, expected_balanced)

    # Test with a bootstrap subsample for multi-output
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    sample_weight = compute_sample_weight("balanced", y, [0, 1, 1, 2, 2, 3])
    assert_array_almost_equal(sample_weight, expected_balanced ** 2)

    # Test with a missing class
    y = np.asarray([1, 1, 1, 2, 2, 2, 3])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])

    # Test with a missing class for multi-output
    y = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1], [2, 2]])
    sample_weight = compute_sample_weight("balanced", y, range(6))
    assert_array_almost_equal(sample_weight, [1., 1., 1., 1., 1., 1., 0.])


def test_compute_sample_weight_errors():
    """
    Test various error conditions for the `compute_sample_weight` function.
    
    This function checks that `compute_sample_weight` raises appropriate
    errors under different scenarios, such as invalid preset strings, incorrect
    sample weights for specific subsets, unsupported data types for multi-output
    cases, and mismatched lengths of sample weight lists.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Raises:
    -------
    ValueError
    - For invalid preset strings.
    -
    """

    # Test compute_sample_weight raises errors expected.
    # Invalid preset string
    y = np.asarray([1, 1, 1, 2, 2, 2])
    y_ = np.asarray([[1, 0], [1, 0], [1, 0], [2, 1], [2, 1], [2, 1]])
    assert_raises(ValueError, compute_sample_weight, "ni", y)
    assert_raises(ValueError, compute_sample_weight, "ni", y, range(4))
    assert_raises(ValueError, compute_sample_weight, "ni", y_)
    assert_raises(ValueError, compute_sample_weight, "ni", y_, range(4))

    # Not "balanced" for subsample
    assert_raises(ValueError,
                  compute_sample_weight, {1: 2, 2: 1}, y, range(4))

    # Not a list or preset for multi-output
    assert_raises(ValueError, compute_sample_weight, {1: 2, 2: 1}, y_)

    # Incorrect length list for multi-output
    assert_raises(ValueError, compute_sample_weight, [{1: 2, 2: 1}], y_)


def test_compute_sample_weight_more_than_32():
    """
    Compute sample weights for balanced class distribution.
    
    This function calculates the sample weights for a dataset with more than 32 distinct classes to achieve a balanced class distribution. It takes an array of target values `y` and an array of indices for subsampling. The function returns an array of sample weights, which are expected to be nearly identical to an array of ones if the class distribution is already balanced.
    
    Parameters:
    -----------
    y : numpy.ndarray
    An array of target values representing
    """

    # Non-regression smoke test for #12146
    y = np.arange(50)  # more than 32 distinct classes
    indices = np.arange(50)  # use subsampling
    weight = compute_sample_weight('balanced', y, indices=indices)
    assert_array_almost_equal(weight, np.ones(y.shape[0]))
