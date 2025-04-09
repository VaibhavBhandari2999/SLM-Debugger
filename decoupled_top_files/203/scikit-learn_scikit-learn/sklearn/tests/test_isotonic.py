import warnings
import numpy as np
import pickle
import copy

import pytest

from sklearn.datasets import make_regression
from sklearn.isotonic import (
    check_increasing,
    isotonic_regression,
    IsotonicRegression,
    _make_unique,
)

from sklearn.utils.validation import check_array
from sklearn.utils._testing import (
    assert_allclose,
    assert_array_equal,
    assert_array_almost_equal,
)
from sklearn.utils import shuffle

from scipy.special import expit


def test_permutation_invariance():
    """
    Test Permutation Invariance of Isotonic Regression.
    
    This function checks whether the `fit` method of IsotonicRegression is
    permutation invariant. It shuffles the input data and sample weights,
    fits the model on both shuffled and unshuffled data, and asserts that the
    transformed outputs are equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `shuffle`: Shuffles the input data and sample weights.
    - `
    """

    # check that fit is permutation invariant.
    # regression test of missing sorting of sample-weights
    ir = IsotonicRegression()
    x = [1, 2, 3, 4, 5, 6, 7]
    y = [1, 41, 51, 1, 2, 5, 24]
    sample_weight = [1, 2, 3, 4, 5, 6, 7]
    x_s, y_s, sample_weight_s = shuffle(x, y, sample_weight, random_state=0)
    y_transformed = ir.fit_transform(x, y, sample_weight=sample_weight)
    y_transformed_s = ir.fit(x_s, y_s, sample_weight=sample_weight_s).transform(x)

    assert_array_equal(y_transformed, y_transformed_s)


def test_check_increasing_small_number_of_samples():
    """
    Check if the given y values are monotonically increasing.
    
    This function takes two lists, `x` and `y`, representing the x-axis and
    corresponding y-axis values respectively. It uses the `check_increasing`
    function to determine if the y values are strictly increasing. If the y
    values are not increasing, a `UserWarning` is raised.
    
    Args:
    x (list): A list of x-axis values.
    y (list): A list of
    """

    x = [0, 1, 2]
    y = [1, 1.1, 1.05]

    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        is_increasing = check_increasing(x, y)

    assert is_increasing


def test_check_increasing_up():
    """
    Check if the given y values are monotonically increasing.
    
    Parameters:
    -----------
    x : list
    The x-coordinates of the data points.
    y : list
    The y-coordinates of the data points.
    
    Returns:
    --------
    bool
    True if the y values are monotonically increasing, False otherwise.
    
    Raises:
    -------
    UserWarning
    If the y values are not monotonically increasing.
    
    Notes:
    ------
    This
    """

    x = [0, 1, 2, 3, 4, 5]
    y = [0, 1.5, 2.77, 8.99, 8.99, 50]

    # Check that we got increasing=True and no warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        is_increasing = check_increasing(x, y)

    assert is_increasing


def test_check_increasing_up_extreme():
    """
    Check if the given data points (x, y) are monotonically increasing.
    
    Parameters:
    -----------
    x : list or array-like
    The x-coordinates of the data points.
    y : list or array-like
    The y-coordinates of the data points.
    
    Returns:
    --------
    is_increasing : bool
    True if the data points are monotonically increasing, False otherwise.
    
    Notes:
    ------
    This function uses the `check_in
    """

    x = [0, 1, 2, 3, 4, 5]
    y = [0, 1, 2, 3, 4, 5]

    # Check that we got increasing=True and no warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        is_increasing = check_increasing(x, y)

    assert is_increasing


def test_check_increasing_down():
    """
    Check if the given y values are decreasing.
    
    Parameters:
    -----------
    x : list
    The x-coordinates of the data points.
    y : list
    The y-coordinates of the data points.
    
    Returns:
    --------
    bool
    True if the y values are decreasing, False otherwise.
    
    Notes:
    ------
    This function uses the `check_increasing` function to determine if the y values are decreasing. It also suppresses any warnings generated during the
    """

    x = [0, 1, 2, 3, 4, 5]
    y = [0, -1.5, -2.77, -8.99, -8.99, -50]

    # Check that we got increasing=False and no warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        is_increasing = check_increasing(x, y)

    assert not is_increasing


def test_check_increasing_down_extreme():
    """
    Check if the given data points are decreasing.
    
    This function evaluates whether the provided y-values are decreasing
    corresponding to the x-values. It uses the `check_increasing` function
    with `increasing=False` to determine the trend of the data.
    
    Parameters:
    x (list): A list of x-values.
    y (list): A list of y-values.
    
    Returns:
    bool: True if the y-values are decreasing, False otherwise.
    
    Notes:
    -
    """

    x = [0, 1, 2, 3, 4, 5]
    y = [0, -1, -2, -3, -4, -5]

    # Check that we got increasing=False and no warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        is_increasing = check_increasing(x, y)

    assert not is_increasing


def test_check_ci_warn():
    """
    Check if the given data points are increasing and generate a confidence interval.
    
    Parameters:
    -----------
    x : list
    The x-coordinates of the data points.
    y : list
    The y-coordinates of the data points.
    
    Returns:
    --------
    bool
    True if the data points are increasing, False otherwise.
    
    Notes:
    ------
    This function checks whether the given data points (x, y) are increasing or not. If the data points are
    """

    x = [0, 1, 2, 3, 4, 5]
    y = [0, -1, 2, -3, 4, -5]

    # Check that we got increasing=False and CI interval warning
    msg = "interval"
    with pytest.warns(UserWarning, match=msg):
        is_increasing = check_increasing(x, y)

    assert not is_increasing


def test_isotonic_regression():
    """
    Test the isotonic regression function.
    
    This function tests the `isotonic_regression` function with various input arrays and checks if the output matches the expected results. It also verifies the functionality of the `IsotonicRegression` class by fitting and transforming data, handling permutations, and ensuring no crash occurs when all x values are equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `isotonic_regression`: Computes the isotonic regression of an array
    """

    y = np.array([3, 7, 5, 9, 8, 7, 10])
    y_ = np.array([3, 6, 6, 8, 8, 8, 10])
    assert_array_equal(y_, isotonic_regression(y))

    y = np.array([10, 0, 2])
    y_ = np.array([4, 4, 4])
    assert_array_equal(y_, isotonic_regression(y))

    x = np.arange(len(y))
    ir = IsotonicRegression(y_min=0.0, y_max=1.0)
    ir.fit(x, y)
    assert_array_equal(ir.fit(x, y).transform(x), ir.fit_transform(x, y))
    assert_array_equal(ir.transform(x), ir.predict(x))

    # check that it is immune to permutation
    perm = np.random.permutation(len(y))
    ir = IsotonicRegression(y_min=0.0, y_max=1.0)
    assert_array_equal(ir.fit_transform(x[perm], y[perm]), ir.fit_transform(x, y)[perm])
    assert_array_equal(ir.transform(x[perm]), ir.transform(x)[perm])

    # check we don't crash when all x are equal:
    ir = IsotonicRegression()
    assert_array_equal(ir.fit_transform(np.ones(len(x)), y), np.mean(y))


def test_isotonic_regression_ties_min():
    """
    Test isotonic regression with ties on the minimum value.
    
    This function tests the isotonic regression algorithm on an example where
    there are ties at the minimum value. The input consists of arrays `x` and
    `y`, where `x` represents the independent variable and `y` represents the
    dependent variable. The expected output is stored in `y_true`.
    
    The function creates an instance of the `IsotonicRegression` class, fits
    the model to the
    """

    # Setup examples with ties on minimum
    x = [1, 1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5, 6]
    y_true = [1.5, 1.5, 3, 4, 5, 6]

    # Check that we get identical results for fit/transform and fit_transform
    ir = IsotonicRegression()
    ir.fit(x, y)
    assert_array_equal(ir.fit(x, y).transform(x), ir.fit_transform(x, y))
    assert_array_equal(y_true, ir.fit_transform(x, y))


def test_isotonic_regression_ties_max():
    """
    Test isotonic regression with ties on the maximum value.
    
    This function evaluates the isotonic regression algorithm on an example
    dataset with tied maximum values. It ensures that the fitted model
    produces consistent results when using both `fit` followed by `transform`
    and `fit_transform` methods. The input consists of a sequence of x-values
    and corresponding y-values with a tie at the maximum. The expected output
    is also provided for validation.
    
    Parameters:
    None
    """

    # Setup examples with ties on maximum
    x = [1, 2, 3, 4, 5, 5]
    y = [1, 2, 3, 4, 5, 6]
    y_true = [1, 2, 3, 4, 5.5, 5.5]

    # Check that we get identical results for fit/transform and fit_transform
    ir = IsotonicRegression()
    ir.fit(x, y)
    assert_array_equal(ir.fit(x, y).transform(x), ir.fit_transform(x, y))
    assert_array_equal(y_true, ir.fit_transform(x, y))


def test_isotonic_regression_ties_secondary_():
    """
    Test isotonic regression fit, transform  and fit_transform
    against the "secondary" ties method and "pituitary" data from R
     "isotone" package, as detailed in: J. d. Leeuw, K. Hornik, P. Mair,
     Isotone Optimization in R: Pool-Adjacent-Violators Algorithm
    (PAVA) and Active Set Methods

    Set values based on pituitary example and
     the following R command detailed in the paper above:
    > library("isotone")
    > data("pituitary")
    > res1 <- gpava(pituitary$age, pituitary$size, ties="secondary")
    > res1$x

    `isotone` version: 1.0-2, 2014-09-07
    R version: R version 3.1.1 (2014-07-10)
    """
    x = [8, 8, 8, 10, 10, 10, 12, 12, 12, 14, 14]
    y = [21, 23.5, 23, 24, 21, 25, 21.5, 22, 19, 23.5, 25]
    y_true = [
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        22.22222,
        24.25,
        24.25,
    ]

    # Check fit, transform and fit_transform
    ir = IsotonicRegression()
    ir.fit(x, y)
    assert_array_almost_equal(ir.transform(x), y_true, 4)
    assert_array_almost_equal(ir.fit_transform(x, y), y_true, 4)


def test_isotonic_regression_with_ties_in_differently_sized_groups():
    """
    Non-regression test to handle issue 9432:
    https://github.com/scikit-learn/scikit-learn/issues/9432

    Compare against output in R:
    > library("isotone")
    > x <- c(0, 1, 1, 2, 3, 4)
    > y <- c(0, 0, 1, 0, 0, 1)
    > res1 <- gpava(x, y, ties="secondary")
    > res1$x

    `isotone` version: 1.1-0, 2015-07-24
    R version: R version 3.3.2 (2016-10-31)
    """
    x = np.array([0, 1, 1, 2, 3, 4])
    y = np.array([0, 0, 1, 0, 0, 1])
    y_true = np.array([0.0, 0.25, 0.25, 0.25, 0.25, 1.0])
    ir = IsotonicRegression()
    ir.fit(x, y)
    assert_array_almost_equal(ir.transform(x), y_true)
    assert_array_almost_equal(ir.fit_transform(x, y), y_true)


def test_isotonic_regression_reversed():
    """
    Performs isotonic regression on a reversed array.
    
    This function applies isotonic regression to a given array `y` with the
    `increasing` parameter set to `False`. The isotonic regression is performed
    using the `IsotonicRegression` class from scikit-learn. The function checks
    if the transformed array `y_` is non-increasing by comparing adjacent elements.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    -
    """

    y = np.array([10, 9, 10, 7, 6, 6.1, 5])
    y_ = IsotonicRegression(increasing=False).fit_transform(np.arange(len(y)), y)
    assert_array_equal(np.ones(y_[:-1].shape), ((y_[:-1] - y_[1:]) >= 0))


def test_isotonic_regression_auto_decreasing():
    """
    Test isotonic regression for auto-decreasing data.
    
    This function tests the `IsotonicRegression` class from scikit-learn on a
    dataset where the target variable (`y`) is expected to be monotonically
    decreasing. The function sets up the data, fits an isotonic regression model,
    and checks if the resulting transformed values are indeed decreasing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `IsotonicRegression`:
    """

    # Set y and x for decreasing
    y = np.array([10, 9, 10, 7, 6, 6.1, 5])
    x = np.arange(len(y))

    # Create model and fit_transform
    ir = IsotonicRegression(increasing="auto")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        y_ = ir.fit_transform(x, y)
        # work-around for pearson divide warnings in scipy <= 0.17.0
        assert all(["invalid value encountered in " in str(warn.message) for warn in w])

    # Check that relationship decreases
    is_increasing = y_[0] < y_[-1]
    assert not is_increasing


def test_isotonic_regression_auto_increasing():
    """
    Test isotonic regression for automatic increasing behavior.
    
    This function evaluates the isotonic regression on a given dataset where the y-values are expected to be automatically increasing based on the input x-values. The function fits the isotonic regression model to the data and checks if the transformed y-values (`y_`) are monotonically increasing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `IsotonicRegression`: A scikit-learn model for isotonic regression
    """

    # Set y and x for decreasing
    y = np.array([5, 6.1, 6, 7, 10, 9, 10])
    x = np.arange(len(y))

    # Create model and fit_transform
    ir = IsotonicRegression(increasing="auto")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        y_ = ir.fit_transform(x, y)
        # work-around for pearson divide warnings in scipy <= 0.17.0
        assert all(["invalid value encountered in " in str(warn.message) for warn in w])

    # Check that relationship increases
    is_increasing = y_[0] < y_[-1]
    assert is_increasing


def test_assert_raises_exceptions():
    """
    Assert that the IsotonicRegression class raises appropriate exceptions for invalid inputs.
    
    This function tests the IsotonicRegression class to ensure it raises the correct exceptions when given invalid inputs. It checks for inconsistent sample sizes, missing or incorrect dimensions, and other potential issues.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the input arrays have inconsistent sample sizes or if the input is not a 1D array.
    
    Functions Used:
    - fit:
    """

    ir = IsotonicRegression()
    rng = np.random.RandomState(42)

    msg = "Found input variables with inconsistent numbers of samples"
    with pytest.raises(ValueError, match=msg):
        ir.fit([0, 1, 2], [5, 7, 3], [0.1, 0.6])

    with pytest.raises(ValueError, match=msg):
        ir.fit([0, 1, 2], [5, 7])

    msg = "X should be a 1d array"
    with pytest.raises(ValueError, match=msg):
        ir.fit(rng.randn(3, 10), [0, 1, 2])

    msg = "Isotonic regression input X should be a 1d array"
    with pytest.raises(ValueError, match=msg):
        ir.transform(rng.randn(3, 10))


def test_isotonic_sample_weight_parameter_default_value():
    """
    Tests the default value of the `sample_weight` parameter in the IsotonicRegression model.
    
    This function verifies that the default value of the `sample_weight` parameter in the IsotonicRegression model is set to one. It does this by fitting the model twice: once with explicitly set `sample_weight` equal to an array of ones, and once with the default value. The function then asserts that the transformed outputs (`y_set_value` and `y_default_value`) are equal, indicating
    """

    # check if default value of sample_weight parameter is one
    ir = IsotonicRegression()
    # random test data
    rng = np.random.RandomState(42)
    n = 100
    x = np.arange(n)
    y = rng.randint(-50, 50, size=(n,)) + 50.0 * np.log(1 + np.arange(n))
    # check if value is correctly used
    weights = np.ones(n)
    y_set_value = ir.fit_transform(x, y, sample_weight=weights)
    y_default_value = ir.fit_transform(x, y)

    assert_array_equal(y_set_value, y_default_value)


def test_isotonic_min_max_boundaries():
    """
    Test the isotonic regression with specified minimum and maximum boundaries.
    
    This function evaluates the `IsotonicRegression` class by setting the
    `y_min` and `y_max` parameters to 2 and 4 respectively. It then fits the
    model on an input array `x` and target array `y`, where both arrays are
    generated using `np.arange`. The expected output is a transformed array
    `y_result` that matches the predefined `y_test`
    """

    # check if min value is used correctly
    ir = IsotonicRegression(y_min=2, y_max=4)
    n = 6
    x = np.arange(n)
    y = np.arange(n)
    y_test = [2, 2, 2, 3, 4, 4]
    y_result = np.round(ir.fit_transform(x, y))
    assert_array_equal(y_result, y_test)


def test_isotonic_sample_weight():
    """
    Test the isotonic regression with sample weights.
    
    This function evaluates the `fit_transform` method of the `IsotonicRegression`
    class using specified input data `x`, `y`, and `sample_weight`. The expected
    output is calculated based on the provided `y` values and the isotonic
    regression model. The function asserts that the received transformed `y`
    values match the expected ones.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions
    """

    ir = IsotonicRegression()
    x = [1, 2, 3, 4, 5, 6, 7]
    y = [1, 41, 51, 1, 2, 5, 24]
    sample_weight = [1, 2, 3, 4, 5, 6, 7]
    expected_y = [1, 13.95, 13.95, 13.95, 13.95, 13.95, 24]
    received_y = ir.fit_transform(x, y, sample_weight=sample_weight)

    assert_array_equal(expected_y, received_y)


def test_isotonic_regression_oob_raise():
    """
    Raises a ValueError when predicting values outside the interpolation range of the fitted IsotonicRegression model.
    
    This function tests the behavior of the `IsotonicRegression` model from scikit-learn when attempting to predict values outside the range of the input data `x`. The model is trained on the given `y` and `x` arrays, and then an attempt is made to predict values at points outside the range of `x`. An exception is expected to be raised indicating that the new values
    """

    # Set y and x
    y = np.array([3, 7, 5, 9, 8, 7, 10])
    x = np.arange(len(y))

    # Create model and fit
    ir = IsotonicRegression(increasing="auto", out_of_bounds="raise")
    ir.fit(x, y)

    # Check that an exception is thrown
    msg = "in x_new is below the interpolation range"
    with pytest.raises(ValueError, match=msg):
        ir.predict([min(x) - 10, max(x) + 10])


def test_isotonic_regression_oob_clip():
    """
    Test isotonic regression with out-of-bounds clipping.
    
    This function evaluates the isotonic regression model's ability to handle
    out-of-bounds values by fitting the model to a given set of data points and
    predicting values outside the range of the training data. The function uses
    the `IsotonicRegression` class from scikit-learn with 'clip' as the
    out-of-bounds strategy.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Set y and x
    y = np.array([3, 7, 5, 9, 8, 7, 10])
    x = np.arange(len(y))

    # Create model and fit
    ir = IsotonicRegression(increasing="auto", out_of_bounds="clip")
    ir.fit(x, y)

    # Predict from  training and test x and check that min/max match.
    y1 = ir.predict([min(x) - 10, max(x) + 10])
    y2 = ir.predict(x)
    assert max(y1) == max(y2)
    assert min(y1) == min(y2)


def test_isotonic_regression_oob_nan():
    """
    Test isotonic regression with out-of-bounds values set to NaN.
    
    This function evaluates an isotonic regression model on out-of-bounds
    values and checks if the predicted values are correctly set to NaN.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `IsotonicRegression`: The isotonic regression model used for fitting.
    - `fit`: Method to fit the isotonic regression model to the data.
    - `predict`: Method
    """

    # Set y and x
    y = np.array([3, 7, 5, 9, 8, 7, 10])
    x = np.arange(len(y))

    # Create model and fit
    ir = IsotonicRegression(increasing="auto", out_of_bounds="nan")
    ir.fit(x, y)

    # Predict from  training and test x and check that we have two NaNs.
    y1 = ir.predict([min(x) - 10, max(x) + 10])
    assert sum(np.isnan(y1)) == 2


def test_isotonic_regression_pickle():
    """
    Test isotonic regression model serialization using Pickle.
    
    This function serializes an isotonic regression model using Pickle and then deserializes it to ensure that the prediction remains consistent before and after serialization.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `IsotonicRegression`: The isotonic regression model used for fitting and predicting.
    - `fit(x, y)`: Fits the isotonic regression model to the input data `x` and
    """

    y = np.array([3, 7, 5, 9, 8, 7, 10])
    x = np.arange(len(y))

    # Create model and fit
    ir = IsotonicRegression(increasing="auto", out_of_bounds="clip")
    ir.fit(x, y)

    ir_ser = pickle.dumps(ir, pickle.HIGHEST_PROTOCOL)
    ir2 = pickle.loads(ir_ser)
    np.testing.assert_array_equal(ir.predict(x), ir2.predict(x))


def test_isotonic_duplicate_min_entry():
    """
    Test the isotonic regression with duplicate minimum entry.
    
    This function tests the isotonic regression model on a dataset where the
    input values are identical and the target values have a duplicate minimum
    entry. The model is expected to handle this scenario without producing any
    infinite predictions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `IsotonicRegression`: The isotonic regression model used for fitting.
    - `fit(x, y)`:
    """

    x = [0, 0, 1]
    y = [0, 0, 1]

    ir = IsotonicRegression(increasing=True, out_of_bounds="clip")
    ir.fit(x, y)
    all_predictions_finite = np.all(np.isfinite(ir.predict(x)))
    assert all_predictions_finite


def test_isotonic_ymin_ymax():
    """
    Test isotonic regression with specified minimum and maximum bounds.
    
    This function tests the `isotonic_regression` function from scikit-learn
    with various configurations of bounds and increasing/decreasing order.
    
    Parameters:
    None
    
    Returns:
    None
    
    Summary:
    The function tests the `isotonic_regression` function by providing an array
    of values `x` and specifying different bounds (`y_min`, `y_max`) and
    increasing/decreasing order. It
    """

    # Test from @NelleV's issue:
    # https://github.com/scikit-learn/scikit-learn/issues/6921
    x = np.array(
        [
            1.263,
            1.318,
            -0.572,
            0.307,
            -0.707,
            -0.176,
            -1.599,
            1.059,
            1.396,
            1.906,
            0.210,
            0.028,
            -0.081,
            0.444,
            0.018,
            -0.377,
            -0.896,
            -0.377,
            -1.327,
            0.180,
        ]
    )
    y = isotonic_regression(x, y_min=0.0, y_max=0.1)

    assert np.all(y >= 0)
    assert np.all(y <= 0.1)

    # Also test decreasing case since the logic there is different
    y = isotonic_regression(x, y_min=0.0, y_max=0.1, increasing=False)

    assert np.all(y >= 0)
    assert np.all(y <= 0.1)

    # Finally, test with only one bound
    y = isotonic_regression(x, y_min=0.0, increasing=False)

    assert np.all(y >= 0)


def test_isotonic_zero_weight_loop():
    """
    Test isotonic regression with zero-weighted samples.
    
    This function tests the `IsotonicRegression` class by fitting the model
    twice with the same input data but different sample weights. The sample
    weights are generated using a uniform distribution and then some weights
    are set to zero. The function ensures that the model does not hang or fail
    when re-fitting with the same data and zero-weighted samples.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Test from @ogrisel's issue:
    # https://github.com/scikit-learn/scikit-learn/issues/4297

    # Get deterministic RNG with seed
    rng = np.random.RandomState(42)

    # Create regression and samples
    regression = IsotonicRegression()
    n_samples = 50
    x = np.linspace(-3, 3, n_samples)
    y = x + rng.uniform(size=n_samples)

    # Get some random weights and zero out
    w = rng.uniform(size=n_samples)
    w[5:8] = 0
    regression.fit(x, y, sample_weight=w)

    # This will hang in failure case.
    regression.fit(x, y, sample_weight=w)


def test_fast_predict():
    """
    Test the equivalence of slower and faster prediction methods for Isotonic Regression.
    
    This function verifies that the faster prediction method does not alter the out-of-sample predictions made by the model. It compares the predictions generated using both the slower and faster methods on a set of test data.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `IsotonicRegression`: The class used for isotonic regression.
    - `_build_y`: Builds the interpolation function with all
    """

    # test that the faster prediction change doesn't
    # affect out-of-sample predictions:
    # https://github.com/scikit-learn/scikit-learn/pull/6206
    rng = np.random.RandomState(123)
    n_samples = 10**3
    # X values over the -10,10 range
    X_train = 20.0 * rng.rand(n_samples) - 10
    y_train = (
        np.less(rng.rand(n_samples), expit(X_train)).astype("int64").astype("float64")
    )

    weights = rng.rand(n_samples)
    # we also want to test that everything still works when some weights are 0
    weights[rng.rand(n_samples) < 0.1] = 0

    slow_model = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")
    fast_model = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")

    # Build interpolation function with ALL input data, not just the
    # non-redundant subset. The following 2 lines are taken from the
    # .fit() method, without removing unnecessary points
    X_train_fit, y_train_fit = slow_model._build_y(
        X_train, y_train, sample_weight=weights, trim_duplicates=False
    )
    slow_model._build_f(X_train_fit, y_train_fit)

    # fit with just the necessary data
    fast_model.fit(X_train, y_train, sample_weight=weights)

    X_test = 20.0 * rng.rand(n_samples) - 10
    y_pred_slow = slow_model.predict(X_test)
    y_pred_fast = fast_model.predict(X_test)

    assert_array_equal(y_pred_slow, y_pred_fast)


def test_isotonic_copy_before_fit():
    """
    Copies an instance of the IsotonicRegression class without fitting it.
    
    This function creates a shallow copy of an IsotonicRegression object using
    the `copy` module, ensuring that the copied object is not fitted. The
    IsotonicRegression model is used for monotonic regression, where the output
    variable is assumed to be a monotonic function of the input variables.
    
    Parameters:
    None
    
    Returns:
    A shallow copy of the IsotonicRegression
    """

    # https://github.com/scikit-learn/scikit-learn/issues/6628
    ir = IsotonicRegression()
    copy.copy(ir)


def test_isotonic_dtype():
    """
    Test the `isotonic_regression` function with different data types.
    
    This function tests the `isotonic_regression` function by passing arrays of
    different integer and floating-point data types. It also checks the behavior
    when sample weights are provided in various formats. The `IsotonicRegression`
    class from scikit-learn is used to fit and predict values, ensuring that the
    output data type matches the expected type based on the input data type.
    
    Parameters:
    """

    y = [2, 1, 4, 3, 5]
    weights = np.array([0.9, 0.9, 0.9, 0.9, 0.9], dtype=np.float64)
    reg = IsotonicRegression()

    for dtype in (np.int32, np.int64, np.float32, np.float64):
        for sample_weight in (None, weights.astype(np.float32), weights):
            y_np = np.array(y, dtype=dtype)
            expected_dtype = check_array(
                y_np, dtype=[np.float64, np.float32], ensure_2d=False
            ).dtype

            res = isotonic_regression(y_np, sample_weight=sample_weight)
            assert res.dtype == expected_dtype

            X = np.arange(len(y)).astype(dtype)
            reg.fit(X, y_np, sample_weight=sample_weight)
            res = reg.predict(X)
            assert res.dtype == expected_dtype


@pytest.mark.parametrize("y_dtype", [np.int32, np.int64, np.float32, np.float64])
def test_isotonic_mismatched_dtype(y_dtype):
    """
    Test isotonic regression with mismatched data types.
    
    This function tests the `IsotonicRegression` class from scikit-learn by fitting
    the model with input data `X` and target data `y`, where `X` has a different
    data type (`np.float32`) than `y`. The function verifies that the predicted
    values have the same data type as the input `X`.
    
    Parameters:
    -----------
    y_dtype : numpy.dtype
    """

    # regression test for #15004
    # check that data are converted when X and y dtype differ
    reg = IsotonicRegression()
    y = np.array([2, 1, 4, 3, 5], dtype=y_dtype)
    X = np.arange(len(y), dtype=np.float32)
    reg.fit(X, y)
    assert reg.predict(X).dtype == X.dtype


def test_make_unique_dtype():
    """
    Generate unique elements from an array while preserving the original data type.
    
    This function takes an array `x`, another array `y` of the same length, and
    a weight array `w`. It returns unique elements from `x` while maintaining
    the original data type. The arrays `y` and `w` are also modified to match
    the indices of the unique elements in `x`.
    
    Parameters:
    -----------
    x : numpy.ndarray
    Input array from
    """

    x_list = [2, 2, 2, 3, 5]
    for dtype in (np.float32, np.float64):
        x = np.array(x_list, dtype=dtype)
        y = x.copy()
        w = np.ones_like(x)
        x, y, w = _make_unique(x, y, w)
        assert_array_equal(x, [2, 3, 5])


@pytest.mark.parametrize("dtype", [np.float64, np.float32])
def test_make_unique_tolerance(dtype):
    """
    Test the `_make_unique` function for handling numerical tolerances.
    
    This function checks that the `_make_unique` function correctly handles
    numerical equalities within the tolerance specified by `np.finfo`.
    
    Parameters
    ----------
    dtype : numpy.dtype
    The data type of the input array.
    
    Returns
    -------
    None
    
    Notes
    -----
    - The input array `x` is an array of floating-point numbers with values
    [0, 1e-
    """

    # Check that equality takes account of np.finfo tolerance
    x = np.array([0, 1e-16, 1, 1 + 1e-14], dtype=dtype)
    y = x.copy()
    w = np.ones_like(x)
    x, y, w = _make_unique(x, y, w)
    if dtype == np.float64:
        x_out = np.array([0, 1, 1 + 1e-14])
    else:
        x_out = np.array([0, 1])
    assert_array_equal(x, x_out)


def test_isotonic_make_unique_tolerance():
    """
    Test the isotonic regression with unique thresholds generation considering a tolerance level.
    
    This function evaluates the isotonic regression model's ability to handle
    duplicate `X` values within a specified tolerance. The model should average
    the corresponding `y` values for these duplicates and generate unique
    thresholds for both `X` and `y`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `IsotonicRegression.fit()`: Fits the isotonic regression
    """

    # Check that averaging of targets for duplicate X is done correctly,
    # taking into account tolerance
    X = np.array([0, 1, 1 + 1e-16, 2], dtype=np.float64)
    y = np.array([0, 1, 2, 3], dtype=np.float64)
    ireg = IsotonicRegression().fit(X, y)
    y_pred = ireg.predict([0, 0.5, 1, 1.5, 2])

    assert_array_equal(y_pred, np.array([0, 0.75, 1.5, 2.25, 3]))
    assert_array_equal(ireg.X_thresholds_, np.array([0.0, 1.0, 2.0]))
    assert_array_equal(ireg.y_thresholds_, np.array([0.0, 1.5, 3.0]))


def test_isotonic_non_regression_inf_slope():
    """
    Ensure that inf values are not returned by the IsotonicRegression model.
    
    This function tests the `IsotonicRegression` model from scikit-learn to
    verify that it does not return infinite (`inf`) values when predicting on
    specific input data points. The input data includes both finite and very
    small values, and the expected output is a finite array of predictions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `Is
    """

    # Non-regression test to ensure that inf values are not returned
    # see: https://github.com/scikit-learn/scikit-learn/issues/10903
    X = np.array([0.0, 4.1e-320, 4.4e-314, 1.0])
    y = np.array([0.42, 0.42, 0.44, 0.44])
    ireg = IsotonicRegression().fit(X, y)
    y_pred = ireg.predict(np.array([0, 2.1e-319, 5.4e-316, 1e-10]))
    assert np.all(np.isfinite(y_pred))


@pytest.mark.parametrize("increasing", [True, False])
def test_isotonic_thresholds(increasing):
    """
    Tests the `IsotonicRegression` class for isotonic regression.
    
    This function evaluates the `IsotonicRegression` class by fitting it to
    randomly generated data and checking the properties of the resulting
    thresholds. The function ensures that the thresholds are correctly
    ordered and within the range of the input data, and that they are a
    strict subset of the training data points.
    
    Parameters:
    -----------
    increasing : bool
    Indicates whether the regression should be increasing
    """

    rng = np.random.RandomState(42)
    n_samples = 30
    X = rng.normal(size=n_samples)
    y = rng.normal(size=n_samples)
    ireg = IsotonicRegression(increasing=increasing).fit(X, y)
    X_thresholds, y_thresholds = ireg.X_thresholds_, ireg.y_thresholds_
    assert X_thresholds.shape == y_thresholds.shape

    # Input thresholds are a strict subset of the training set (unless
    # the data is already strictly monotonic which is not the case with
    # this random data)
    assert X_thresholds.shape[0] < X.shape[0]
    assert np.in1d(X_thresholds, X).all()

    # Output thresholds lie in the range of the training set:
    assert y_thresholds.max() <= y.max()
    assert y_thresholds.min() >= y.min()

    assert all(np.diff(X_thresholds) > 0)
    if increasing:
        assert all(np.diff(y_thresholds) >= 0)
    else:
        assert all(np.diff(y_thresholds) <= 0)


def test_input_shape_validation():
    """
    Test input shape validation for IsotonicRegression.
    
    This function tests whether IsotonicRegression can handle a 2D array with
    only one feature. It fits the model on both 1D and 2D arrays of the same
    data and compares the results.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords and Functions:
    - `IsotonicRegression`: The scikit-learn model used for isotonic regression.
    - `fit`:
    """

    # Test from #15012
    # Check that IsotonicRegression can handle 2darray with only 1 feature
    X = np.arange(10)
    X_2d = X.reshape(-1, 1)
    y = np.arange(10)

    iso_reg = IsotonicRegression().fit(X, y)
    iso_reg_2d = IsotonicRegression().fit(X_2d, y)

    assert iso_reg.X_max_ == iso_reg_2d.X_max_
    assert iso_reg.X_min_ == iso_reg_2d.X_min_
    assert iso_reg.y_max == iso_reg_2d.y_max
    assert iso_reg.y_min == iso_reg_2d.y_min
    assert_array_equal(iso_reg.X_thresholds_, iso_reg_2d.X_thresholds_)
    assert_array_equal(iso_reg.y_thresholds_, iso_reg_2d.y_thresholds_)

    y_pred1 = iso_reg.predict(X)
    y_pred2 = iso_reg_2d.predict(X_2d)
    assert_allclose(y_pred1, y_pred2)


def test_isotonic_2darray_more_than_1_feature():
    """
    Ensures that the `IsotonicRegression` model raises a ValueError when fitting or predicting on a 2D array with more than one feature.
    
    This function tests the behavior of the `IsotonicRegression` model from scikit-learn when given a 2D array with more than one feature. It verifies that the model correctly raises a ValueError with an appropriate message indicating that the input should be a 1D array or a 2D array with only one feature.
    
    Parameters
    """

    # Ensure IsotonicRegression raises error if input has more than 1 feature
    X = np.arange(10)
    X_2d = np.c_[X, X]
    y = np.arange(10)

    msg = "should be a 1d array or 2d array with 1 feature"
    with pytest.raises(ValueError, match=msg):
        IsotonicRegression().fit(X_2d, y)

    iso_reg = IsotonicRegression().fit(X, y)
    with pytest.raises(ValueError, match=msg):
        iso_reg.predict(X_2d)

    with pytest.raises(ValueError, match=msg):
        iso_reg.transform(X_2d)


def test_isotonic_regression_sample_weight_not_overwritten():
    """Check that calling fitting function of isotonic regression will not
    overwrite `sample_weight`.
    Non-regression test for:
    https://github.com/scikit-learn/scikit-learn/issues/20508
    """
    X, y = make_regression(n_samples=10, n_features=1, random_state=41)
    sample_weight_original = np.ones_like(y)
    sample_weight_original[0] = 10
    sample_weight_fit = sample_weight_original.copy()

    isotonic_regression(y, sample_weight=sample_weight_fit)
    assert_allclose(sample_weight_fit, sample_weight_original)

    IsotonicRegression().fit(X, y, sample_weight=sample_weight_fit)
    assert_allclose(sample_weight_fit, sample_weight_original)


@pytest.mark.parametrize("shape", ["1d", "2d"])
def test_get_feature_names_out(shape):
    """Check `get_feature_names_out` for `IsotonicRegression`."""
    X = np.arange(10)
    if shape == "2d":
        X = X.reshape(-1, 1)
    y = np.arange(10)

    iso = IsotonicRegression().fit(X, y)
    names = iso.get_feature_names_out()
    assert isinstance(names, np.ndarray)
    assert names.dtype == object
    assert_array_equal(["isotonicregression0"], names)
