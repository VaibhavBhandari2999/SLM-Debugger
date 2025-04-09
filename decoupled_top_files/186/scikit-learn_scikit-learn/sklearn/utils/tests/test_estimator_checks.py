import unittest
import sys

import numpy as np
import scipy.sparse as sp

from sklearn.externals.six.moves import cStringIO as StringIO
from sklearn.externals import joblib

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import deprecated
from sklearn.utils.testing import (assert_raises_regex, assert_true,
                                   assert_equal, ignore_warnings)
from sklearn.utils.estimator_checks import check_estimator
from sklearn.utils.estimator_checks import set_random_state
from sklearn.utils.estimator_checks import set_checking_parameters
from sklearn.utils.estimator_checks import check_estimators_unfitted
from sklearn.utils.estimator_checks import check_fit_score_takes_y
from sklearn.utils.estimator_checks import check_no_attributes_set_in_init
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression, SGDClassifier
from sklearn.mixture import GaussianMixture
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import NMF
from sklearn.linear_model import MultiTaskElasticNet
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsRegressor
from sklearn.utils.validation import (check_X_y, check_array,
                                      LARGE_SPARSE_SUPPORTED)


class CorrectNotFittedError(ValueError):
    """Exception class to raise if estimator is used before fitting.

    Like NotFittedError, it inherits from ValueError, but not from
    AttributeError. Used for testing only.
    """


class BaseBadClassifier(BaseEstimator, ClassifierMixin):
    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.ones(X.shape[0])


class ChangesDict(BaseEstimator):
    def __init__(self, key=0):
        self.key = key

    def fit(self, X, y=None):
        X, y = check_X_y(X, y)
        return self

    def predict(self, X):
        """
        Predicts the output for the given input data.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
        The input samples.
        
        Returns:
        --------
        np.ndarray : shape (n_samples,)
        An array of ones with the same number of samples as the input data.
        
        Notes:
        ------
        - The input data is first checked using `check_array` to ensure it meets the expected format.
        - A unique key (`self
        """

        X = check_array(X)
        self.key = 1000
        return np.ones(X.shape[0])


class SetsWrongAttribute(BaseEstimator):
    def __init__(self, acceptable_key=0):
        self.acceptable_key = acceptable_key

    def fit(self, X, y=None):
        """
        Fits the model to the training data.
        
        Parameters:
        -----------
        X : array-like or sparse matrix of shape (n_samples, n_features)
        Training data.
        
        y : array-like of shape (n_samples,) or None, default=None
        Target values. If None, the model will be fitted without target values.
        
        Returns:
        --------
        self : object
        The fitted model instance.
        
        Notes:
        ------
        - The `check_X_y` function
        """

        self.wrong_attribute = 0
        X, y = check_X_y(X, y)
        return self


class ChangesWrongAttribute(BaseEstimator):
    def __init__(self, wrong_attribute=0):
        self.wrong_attribute = wrong_attribute

    def fit(self, X, y=None):
        """
        Fits the model to the training data.
        
        Parameters:
        -----------
        X : array-like or sparse matrix of shape (n_samples, n_features)
        Training data.
        
        y : array-like of shape (n_samples,) or (n_samples, n_outputs), optional (default=None)
        Target values.
        
        Returns:
        --------
        self : object
        Fitted estimator.
        
        Notes:
        ------
        - The `wrong_attribute` attribute is set to 1 during fitting
        """

        self.wrong_attribute = 1
        X, y = check_X_y(X, y)
        return self


class ChangesUnderscoreAttribute(BaseEstimator):
    def fit(self, X, y=None):
        """
        Fits the model to the training data.
        
        Parameters:
        -----------
        X : array-like or sparse matrix of shape (n_samples, n_features)
        The training input samples.
        y : array-like of shape (n_samples,) or (n_samples, n_outputs), default=None
        The target values (class labels in classification, real numbers in regression).
        
        Returns:
        --------
        self : object
        The fitted estimator.
        
        Notes:
        ------
        - The `_
        """

        self._good_attribute = 1
        X, y = check_X_y(X, y)
        return self


class NoCheckinPredict(BaseBadClassifier):
    def fit(self, X, y):
        X, y = check_X_y(X, y)
        return self


class NoSparseClassifier(BaseBadClassifier):
    def fit(self, X, y):
        """
        Fit the model to data matrix X and target(s) y.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        Training data.
        y : array-like of shape (n_samples,) or (n_samples, n_targets)
        Target values.
        
        Returns
        -------
        self : object
        Fitted estimator.
        
        Raises
        ------
        ValueError
        If the input data matrix X is sparse.
        """

        X, y = check_X_y(X, y, accept_sparse=['csr', 'csc'])
        if sp.issparse(X):
            raise ValueError("Nonsensical Error")
        return self

    def predict(self, X):
        X = check_array(X)
        return np.ones(X.shape[0])


class CorrectNotFittedErrorClassifier(BaseBadClassifier):
    def fit(self, X, y):
        """
        Fit the model using the given training data.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
        Training data.
        y : array-like, shape (n_samples,)
        Target values.
        
        Returns:
        --------
        self : object
        Fitted model.
        
        Notes:
        ------
        - The function uses `check_X_y` to validate and convert the input data.
        - It initializes the coefficients (`coef_`) to an array
        """

        X, y = check_X_y(X, y)
        self.coef_ = np.ones(X.shape[1])
        return self

    def predict(self, X):
        """
        Predicts the target values for the given input data.
        
        This function takes an input array `X` and returns an array of ones with the same number of rows as `X`. The prediction is based on the previously fitted model coefficients (`coef_`). If the model has not been fitted yet, a `CorrectNotFittedError` is raised.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
        The input samples.
        
        Returns:
        """

        if not hasattr(self, 'coef_'):
            raise CorrectNotFittedError("estimator is not fitted yet")
        X = check_array(X)
        return np.ones(X.shape[0])


class NoSampleWeightPandasSeriesType(BaseEstimator):
    def fit(self, X, y, sample_weight=None):
        """
        Fits the model to the training data.
        
        Parameters:
        -----------
        X : array-like or sparse matrix of shape (n_samples, n_features)
        Training data.
        y : array-like of shape (n_samples,) or (n_samples, n_targets)
        Target values.
        sample_weight : array-like of shape (n_samples,), default=None
        Sample weights.
        
        Returns:
        --------
        self : object
        The fitted estimator.
        
        Notes:
        ------
        """

        # Convert data
        X, y = check_X_y(X, y,
                         accept_sparse=("csr", "csc"),
                         multi_output=True,
                         y_numeric=True)
        # Function is only called after we verify that pandas is installed
        from pandas import Series
        if isinstance(sample_weight, Series):
            raise ValueError("Estimator does not accept 'sample_weight'"
                             "of type pandas.Series")
        return self

    def predict(self, X):
        X = check_array(X)
        return np.ones(X.shape[0])


class BadTransformerWithoutMixin(BaseEstimator):
    def fit(self, X, y=None):
        X = check_array(X)
        return self

    def transform(self, X):
        X = check_array(X)
        return X


class NotInvariantPredict(BaseEstimator):
    def fit(self, X, y):
        """
        Fit the model according to the given training data.
        
        Parameters:
        -----------
        X : array-like or sparse matrix of shape (n_samples, n_features)
        Training vector, where `n_samples` is the number of samples and
        `n_features` is the number of features.
        
        y : array-like of shape (n_samples,) or (n_samples, n_outputs)
        Target values (class labels in classification, real numbers in
        regression).
        
        Returns:
        --------
        """

        # Convert data
        X, y = check_X_y(X, y,
                         accept_sparse=("csr", "csc"),
                         multi_output=True,
                         y_numeric=True)
        return self

    def predict(self, X):
        """
        Predicts the output based on the input data.
        
        This function checks if the input array `X` contains more than one element along the first axis (rows). If so, it returns an array of ones with the same number of elements as `X`. Otherwise, it returns an array of zeros with the same number of elements as `X`.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples,)
        The input data points.
        
        Returns:
        --------
        numpy
        """

        # return 1 if X has more than one element else return 0
        X = check_array(X)
        if X.shape[0] > 1:
            return np.ones(X.shape[0])
        return np.zeros(X.shape[0])


class LargeSparseNotSupportedClassifier(BaseEstimator):
    def fit(self, X, y):
        """
        Ensures that the input data meets the required specifications and formats.
        
        This method checks the input data `X` and target variable `y` to ensure they meet the necessary conditions for fitting the model. It validates the data types, formats, and ensures compatibility with the estimator.
        
        Parameters
        ----------
        X : array-like or sparse matrix
        The input features of shape (n_samples, n_features).
        y : array-like
        The target values of shape (n_samples,) or
        """

        X, y = check_X_y(X, y,
                         accept_sparse=("csr", "csc", "coo"),
                         accept_large_sparse=True,
                         multi_output=True,
                         y_numeric=True)
        if sp.issparse(X):
            if X.getformat() == "coo":
                if X.row.dtype == "int64" or X.col.dtype == "int64":
                    raise ValueError(
                        "Estimator doesn't support 64-bit indices")
            elif X.getformat() in ["csc", "csr"]:
                if X.indices.dtype == "int64" or X.indptr.dtype == "int64":
                    raise ValueError(
                        "Estimator doesn't support 64-bit indices")

        return self


class SparseTransformer(BaseEstimator):
    def fit(self, X, y=None):
        self.X_shape_ = check_array(X).shape
        return self

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def transform(self, X):
        """
        Transforms the input data `X` into a sparse CSR matrix.
        
        Parameters:
        -----------
        X : array-like, shape (n_samples, n_features)
        The input data to be transformed.
        
        Returns:
        --------
        csr_matrix : scipy.sparse.csr.csr_matrix
        The transformed input data represented as a sparse CSR matrix.
        
        Raises:
        -------
        ValueError
        If the number of features in `X` does not match the expected number of features (`self.X
        """

        X = check_array(X)
        if X.shape[1] != self.X_shape_[1]:
            raise ValueError('Bad number of features')
        return sp.csr_matrix(X)


def test_check_fit_score_takes_y_works_on_deprecated_fit():
    """
    Tests whether the `check_fit_score_takes_y` function correctly identifies that the `fit` method of `TestEstimatorWithDeprecatedFitMethod` accepts target variable `y`. The `TestEstimatorWithDeprecatedFitMethod` is designed to have a deprecated `fit` method that takes both features `X` and target `y`, ensuring that `check_fit_score_takes_y` can validate this behavior.
    
    Args:
    estimator_name (str): The name of the estimator being tested.
    """

    # Tests that check_fit_score_takes_y works on a class with
    # a deprecated fit method

    class TestEstimatorWithDeprecatedFitMethod(BaseEstimator):
        @deprecated("Deprecated for the purpose of testing "
                    "check_fit_score_takes_y")
        def fit(self, X, y):
            return self

    check_fit_score_takes_y("test", TestEstimatorWithDeprecatedFitMethod())


def test_check_estimator():
    """
    This function tests various aspects of an estimator to ensure it meets certain criteria. It checks for the presence of necessary methods such as `get_params`, `fit`, and `predict`. It also verifies that the estimator handles input validation correctly, maintains its state during predictions, and does not add public attributes during the fitting process. Additionally, it checks for the correct handling of sparse matrices and large sparse matrices, and ensures that the estimator does not change its behavior when applied to subsets of data. The function uses
    """

    # tests that the estimator actually fails on "bad" estimators.
    # not a complete test of all checks, which are very extensive.

    # check that we have a set_params and can clone
    msg = "it does not implement a 'get_params' methods"
    assert_raises_regex(TypeError, msg, check_estimator, object)
    assert_raises_regex(TypeError, msg, check_estimator, object())
    # check that we have a fit method
    msg = "object has no attribute 'fit'"
    assert_raises_regex(AttributeError, msg, check_estimator, BaseEstimator)
    assert_raises_regex(AttributeError, msg, check_estimator, BaseEstimator())
    # check that fit does input validation
    msg = "TypeError not raised"
    assert_raises_regex(AssertionError, msg, check_estimator,
                        BaseBadClassifier)
    assert_raises_regex(AssertionError, msg, check_estimator,
                        BaseBadClassifier())
    # check that sample_weights in fit accepts pandas.Series type
    try:
        from pandas import Series  # noqa
        msg = ("Estimator NoSampleWeightPandasSeriesType raises error if "
               "'sample_weight' parameter is of type pandas.Series")
        assert_raises_regex(
            ValueError, msg, check_estimator, NoSampleWeightPandasSeriesType)
    except ImportError:
        pass
    # check that predict does input validation (doesn't accept dicts in input)
    msg = "Estimator doesn't check for NaN and inf in predict"
    assert_raises_regex(AssertionError, msg, check_estimator, NoCheckinPredict)
    assert_raises_regex(AssertionError, msg, check_estimator,
                        NoCheckinPredict())
    # check that estimator state does not change
    # at transform/predict/predict_proba time
    msg = 'Estimator changes __dict__ during predict'
    assert_raises_regex(AssertionError, msg, check_estimator, ChangesDict)
    # check that `fit` only changes attribures that
    # are private (start with an _ or end with a _).
    msg = ('Estimator ChangesWrongAttribute should not change or mutate  '
           'the parameter wrong_attribute from 0 to 1 during fit.')
    assert_raises_regex(AssertionError, msg,
                        check_estimator, ChangesWrongAttribute)
    check_estimator(ChangesUnderscoreAttribute)
    # check that `fit` doesn't add any public attribute
    msg = (r'Estimator adds public attribute\(s\) during the fit method.'
           ' Estimators are only allowed to add private attributes'
           ' either started with _ or ended'
           ' with _ but wrong_attribute added')
    assert_raises_regex(AssertionError, msg,
                        check_estimator, SetsWrongAttribute)
    # check for invariant method
    name = NotInvariantPredict.__name__
    method = 'predict'
    msg = ("{method} of {name} is not invariant when applied "
           "to a subset.").format(method=method, name=name)
    assert_raises_regex(AssertionError, msg,
                        check_estimator, NotInvariantPredict)
    # check for sparse matrix input handling
    name = NoSparseClassifier.__name__
    msg = "Estimator %s doesn't seem to fail gracefully on sparse data" % name
    # the check for sparse input handling prints to the stdout,
    # instead of raising an error, so as not to remove the original traceback.
    # that means we need to jump through some hoops to catch it.
    old_stdout = sys.stdout
    string_buffer = StringIO()
    sys.stdout = string_buffer
    try:
        check_estimator(NoSparseClassifier)
    except:
        pass
    finally:
        sys.stdout = old_stdout
    assert_true(msg in string_buffer.getvalue())

    # Large indices test on bad estimator
    msg = ('Estimator LargeSparseNotSupportedClassifier doesn\'t seem to '
           r'support \S{3}_64 matrix, and is not failing gracefully.*')
    # only supported by scipy version more than 0.14.0
    if LARGE_SPARSE_SUPPORTED:
        assert_raises_regex(AssertionError, msg, check_estimator,
                            LargeSparseNotSupportedClassifier)

    # non-regression test for estimators transforming to sparse data
    check_estimator(SparseTransformer())

    # doesn't error on actual estimator
    check_estimator(AdaBoostClassifier)
    check_estimator(AdaBoostClassifier())
    check_estimator(MultiTaskElasticNet)
    check_estimator(MultiTaskElasticNet())


def test_check_estimator_transformer_no_mixin():
    """
    Tests the ability of the `check_estimator` function to handle transformers without the TransformerMixin.
    
    This function verifies that the `check_estimator` function can successfully run tests on a transformer class that does not inherit from TransformerMixin, ensuring that the absence of this mixin does not prevent the execution of fit_transform method checks.
    """

    # check that TransformerMixin is not required for transformer tests to run
    assert_raises_regex(AttributeError, '.*fit_transform.*',
                        check_estimator, BadTransformerWithoutMixin())


def test_check_estimator_clones():
    """
    Test that check_estimator does not modify the provided estimator.
    
    This function checks whether the `check_estimator` function alters the
    state of the estimator it receives, both before and after fitting the data.
    It iterates over several different estimators (GaussianMixture, LinearRegression,
    RandomForestClassifier, NMF, SGDClassifier, MiniBatchKMeans) and ensures that
    the hash value of the estimator remains unchanged after running `check_estimator`
    on it, both in cases
    """

    # check that check_estimator doesn't modify the estimator it receives
    from sklearn.datasets import load_iris
    iris = load_iris()

    for Estimator in [GaussianMixture, LinearRegression,
                      RandomForestClassifier, NMF, SGDClassifier,
                      MiniBatchKMeans]:
        with ignore_warnings(category=FutureWarning):
            # when 'est = SGDClassifier()'
            est = Estimator()
        set_checking_parameters(est)
        set_random_state(est)
        # without fitting
        old_hash = joblib.hash(est)
        check_estimator(est)
        assert_equal(old_hash, joblib.hash(est))

        with ignore_warnings(category=FutureWarning):
            # when 'est = SGDClassifier()'
            est = Estimator()
        set_checking_parameters(est)
        set_random_state(est)
        # with fitting
        est.fit(iris.data + 10, iris.target)
        old_hash = joblib.hash(est)
        check_estimator(est)
        assert_equal(old_hash, joblib.hash(est))


def test_check_estimators_unfitted():
    """
    Raise a ValueError or AttributeError when calling predict on an unfitted estimator. This function tests whether an estimator raises the correct error when attempting to use `predict` on an unfitted model. It checks both `ValueError` and `AttributeError`, ensuring that the appropriate exception is raised.
    
    Parameters:
    -----------
    estimator : str
    The name of the estimator to be tested.
    classifier : object
    The classifier instance to be tested.
    
    Returns:
    --------
    None
    """

    # check that a ValueError/AttributeError is raised when calling predict
    # on an unfitted estimator
    msg = "AttributeError or ValueError not raised by predict"
    assert_raises_regex(AssertionError, msg, check_estimators_unfitted,
                        "estimator", NoSparseClassifier())

    # check that CorrectNotFittedError inherit from either ValueError
    # or AttributeError
    check_estimators_unfitted("estimator", CorrectNotFittedErrorClassifier())


def test_check_no_attributes_set_in_init():
    """
    Assert that an estimator does not set any attributes other than parameters during initialization.
    
    This function checks if the given estimator sets any attributes other than parameters during its initialization. It raises an AssertionError with a specific message if such attributes are found.
    
    Parameters
    ----------
    estimator_name : str
    The name of the estimator being checked.
    estimator_class : object
    The estimator class to be checked.
    
    Raises
    ------
    AssertionError
    If the estimator sets any attributes other than parameters
    """

    class NonConformantEstimatorPrivateSet(object):
        def __init__(self):
            self.you_should_not_set_this_ = None

    class NonConformantEstimatorNoParamSet(object):
        def __init__(self, you_should_set_this_=None):
            pass

    assert_raises_regex(AssertionError,
                        "Estimator estimator_name should not set any"
                        " attribute apart from parameters during init."
                        r" Found attributes \['you_should_not_set_this_'\].",
                        check_no_attributes_set_in_init,
                        'estimator_name',
                        NonConformantEstimatorPrivateSet())
    assert_raises_regex(AssertionError,
                        "Estimator estimator_name should store all "
                        "parameters as an attribute during init. "
                        "Did not find attributes "
                        r"\['you_should_set_this_'\].",
                        check_no_attributes_set_in_init,
                        'estimator_name',
                        NonConformantEstimatorNoParamSet())


def test_check_estimator_pairwise():
    """
    Tests the `check_estimator` function for estimators using pairwise kernels or metrics.
    
    This function verifies that the `check_estimator` function correctly validates
    estimators that utilize either a precomputed kernel or a precomputed metric.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `check_estimator`: Validates an estimator object.
    
    Key Estimators:
    - `SVC(kernel='precomputed')`: Support Vector Classifier with a precomputed kernel.
    -
    """

    # check that check_estimator() works on estimator with _pairwise
    # kernel or  metric

    # test precomputed kernel
    est = SVC(kernel='precomputed')
    check_estimator(est)

    # test precomputed metric
    est = KNeighborsRegressor(metric='precomputed')
    check_estimator(est)


def run_tests_without_pytest():
    """Runs the tests in this file without using pytest.
    """
    main_module = sys.modules['__main__']
    test_functions = [getattr(main_module, name) for name in dir(main_module)
                      if name.startswith('test_')]
    test_cases = [unittest.FunctionTestCase(fn) for fn in test_functions]
    suite = unittest.TestSuite()
    suite.addTests(test_cases)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    # This module is run as a script to check that we have no dependency on
    # pytest for estimator checks.
    run_tests_without_pytest()
