import unittest
import sys

import numpy as np
import scipy.sparse as sp

from io import StringIO

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import deprecated
from sklearn.utils import _joblib
from sklearn.utils.testing import (assert_raises_regex,
                                   assert_equal, ignore_warnings,
                                   assert_warns, assert_raises)
from sklearn.utils.estimator_checks import check_estimator
from sklearn.utils.estimator_checks \
    import check_class_weight_balanced_linear_classifier
from sklearn.utils.estimator_checks import set_random_state
from sklearn.utils.estimator_checks import set_checking_parameters
from sklearn.utils.estimator_checks import check_estimators_unfitted
from sklearn.utils.estimator_checks import check_fit_score_takes_y
from sklearn.utils.estimator_checks import check_no_attributes_set_in_init
from sklearn.utils.estimator_checks import check_outlier_corruption
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression, SGDClassifier
from sklearn.mixture import GaussianMixture
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import NMF
from sklearn.linear_model import MultiTaskElasticNet
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsRegressor
from sklearn.utils.validation import check_X_y, check_array


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
        X = check_array(X)
        self.key = 1000
        return np.ones(X.shape[0])


class SetsWrongAttribute(BaseEstimator):
    def __init__(self, acceptable_key=0):
        self.acceptable_key = acceptable_key

    def fit(self, X, y=None):
        """
        Fit the model to the training data.
        
        Parameters:
        X (array-like): The input features of the training data.
        y (array-like, optional): The target labels of the training data. If not provided, the model assumes unsupervised learning.
        
        Returns:
        self: The fitted model.
        
        Attributes:
        wrong_attribute (int): A placeholder attribute that is set to 0 during the fitting process.
        """

        self.wrong_attribute = 0
        X, y = check_X_y(X, y)
        return self


class ChangesWrongAttribute(BaseEstimator):
    def __init__(self, wrong_attribute=0):
        self.wrong_attribute = wrong_attribute

    def fit(self, X, y=None):
        """
        Fit the model to data matrix X and target(s) y.
        
        Parameters:
        X (array-like): The input data matrix of shape (n_samples, n_features).
        y (array-like, optional): The target values of shape (n_samples,) or (n_samples, n_targets). If None, the model will be fit without target values.
        
        Returns:
        self: The fitted model.
        """

        self.wrong_attribute = 1
        X, y = check_X_y(X, y)
        return self


class ChangesUnderscoreAttribute(BaseEstimator):
    def fit(self, X, y=None):
        self._good_attribute = 1
        X, y = check_X_y(X, y)
        return self


class RaisesErrorInSetParams(BaseEstimator):
    def __init__(self, p=0):
        self.p = p

    def set_params(self, **kwargs):
        if 'p' in kwargs:
            p = kwargs.pop('p')
            if p < 0:
                raise ValueError("p can't be less than 0")
            self.p = p
        return super().set_params(**kwargs)

    def fit(self, X, y=None):
        X, y = check_X_y(X, y)
        return self


class ModifiesValueInsteadOfRaisingError(BaseEstimator):
    def __init__(self, p=0):
        self.p = p

    def set_params(self, **kwargs):
        if 'p' in kwargs:
            p = kwargs.pop('p')
            if p < 0:
                p = 0
            self.p = p
        return super().set_params(**kwargs)

    def fit(self, X, y=None):
        X, y = check_X_y(X, y)
        return self


class ModifiesAnotherValue(BaseEstimator):
    def __init__(self, a=0, b='method1'):
        self.a = a
        self.b = b

    def set_params(self, **kwargs):
        if 'a' in kwargs:
            a = kwargs.pop('a')
            self.a = a
            if a is None:
                kwargs.pop('b')
                self.b = 'method2'
        return super().set_params(**kwargs)

    def fit(self, X, y=None):
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
        
        Parameters:
        X (array-like, shape (n_samples, n_features)): The input data.
        y (array-like, shape (n_samples,) or (n_samples, n_outputs)): The target values.
        
        Returns:
        self (object): The fitted estimator.
        
        Raises:
        ValueError: If the input data matrix X is sparse.
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
        Fit the model to data matrix X and target(s) y.
        
        Parameters:
        X (array-like, shape (n_samples, n_features)): The input data.
        y (array-like, shape (n_samples,) or (n_samples, n_targets)): The target values.
        
        Returns:
        self (object): The fitted model.
        """

        X, y = check_X_y(X, y)
        self.coef_ = np.ones(X.shape[1])
        return self

    def predict(self, X):
        if not hasattr(self, 'coef_'):
            raise CorrectNotFittedError("estimator is not fitted yet")
        X = check_array(X)
        return np.ones(X.shape[0])


class NoSampleWeightPandasSeriesType(BaseEstimator):
    def fit(self, X, y, sample_weight=None):
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


class BadBalancedWeightsClassifier(BaseBadClassifier):
    def __init__(self, class_weight=None):
        self.class_weight = class_weight

    def fit(self, X, y):
        from sklearn.preprocessing import LabelEncoder
        from sklearn.utils import compute_class_weight

        label_encoder = LabelEncoder().fit(y)
        classes = label_encoder.classes_
        class_weight = compute_class_weight(self.class_weight, classes, y)

        # Intentionally modify the balanced class_weight
        # to simulate a bug and raise an exception
        if self.class_weight == "balanced":
            class_weight += 1.

        # Simply assigning coef_ to the class_weight
        self.coef_ = class_weight
        return self


class BadTransformerWithoutMixin(BaseEstimator):
    def fit(self, X, y=None):
        X = check_array(X)
        return self

    def transform(self, X):
        X = check_array(X)
        return X


class NotInvariantPredict(BaseEstimator):
    def fit(self, X, y):
        # Convert data
        X, y = check_X_y(X, y,
                         accept_sparse=("csr", "csc"),
                         multi_output=True,
                         y_numeric=True)
        return self

    def predict(self, X):
        """
        Predict the output based on the input data.
        
        Parameters:
        X (array-like): Input data for prediction. It can be a 1D or 2D array.
        
        Returns:
        array-like: An array of predictions. Returns an array of ones if the input has more than one row, otherwise returns an array of zeros.
        
        Notes:
        - The input X is first converted to a NumPy array using check_array function.
        - If the number of rows in X is greater than
        """

        # return 1 if X has more than one element else return 0
        X = check_array(X)
  
