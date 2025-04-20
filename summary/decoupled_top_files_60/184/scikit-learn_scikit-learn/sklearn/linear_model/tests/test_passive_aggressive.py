from sklearn.utils.testing import assert_true
import numpy as np
import scipy.sparse as sp

from sklearn.utils.testing import assert_less
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import assert_array_almost_equal, assert_array_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_raises

from sklearn.base import ClassifierMixin
from sklearn.utils import check_random_state
from sklearn.datasets import load_iris
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import PassiveAggressiveRegressor

iris = load_iris()
random_state = check_random_state(12)
indices = np.arange(iris.data.shape[0])
random_state.shuffle(indices)
X = iris.data[indices]
y = iris.target[indices]
X_csr = sp.csr_matrix(X)


class MyPassiveAggressive(ClassifierMixin):

    def __init__(self, C=1.0, epsilon=0.01, loss="hinge",
                 fit_intercept=True, n_iter=1, random_state=None):
        self.C = C
        self.epsilon = epsilon
        self.loss = loss
        self.fit_intercept = fit_intercept
        self.n_iter = n_iter

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features, dtype=np.float64)
        self.b = 0.0

        for t in range(self.n_iter):
            for i in range(n_samples):
                p = self.project(X[i])
                if self.loss in ("hinge", "squared_hinge"):
                    loss = max(1 - y[i] * p, 0)
                else:
                    loss = max(np.abs(p - y[i]) - self.epsilon, 0)

                sqnorm = np.dot(X[i], X[i])

                if self.loss in ("hinge", "epsilon_insensitive"):
                    step = min(self.C, loss / sqnorm)
                elif self.loss in ("squared_hinge",
                                   "squared_epsilon_insensitive"):
                    step = loss / (sqnorm + 1.0 / (2 * self.C))

                if self.loss in ("hinge", "squared_hinge"):
                    step *= y[i]
                else:
                    step *= np.sign(y[i] - p)

                self.w += step * X[i]
                if self.fit_intercept:
                    self.b += step

    def project(self, X):
        return np.dot(X, self.w) + self.b


def test_classifier_accuracy():
    """
    Test the accuracy of the PassiveAggressiveClassifier.
    
    This function evaluates the performance of the PassiveAggressiveClassifier
    on given data. It iterates over different configurations of the data type,
    fit intercept, and averaging options to ensure the classifier meets a
    minimum accuracy threshold.
    
    Parameters:
    X (array-like or sparse matrix): The input features for training and
    testing the classifier.
    X_csr (array-like or sparse matrix): Another input features for training
    and testing the classifier,
    """

    for data in (X, X_csr):
        for fit_intercept in (True, False):
            for average in (False, True):
                clf = PassiveAggressiveClassifier(
                    C=1.0, max_iter=30, fit_intercept=fit_intercept,
                    random_state=0, average=average, tol=None)
                clf.fit(data, y)
                score = clf.score(data, y)
                assert_greater(score, 0.79)
                if average:
                    assert_true(hasattr(clf, 'average_coef_'))
                    assert_true(hasattr(clf, 'average_intercept_'))
                    assert_true(hasattr(clf, 'standard_intercept_'))
                    assert_true(hasattr(clf, 'standard_coef_'))


def test_classifier_partial_fit():
    classes = np.unique(y)
    for data in (X, X_csr):
        for average in (False, True):
            clf = PassiveAggressiveClassifier(
                C=1.0, fit_intercept=True, random_state=0,
                average=average, max_iter=5)
            for t in range(30):
                clf.partial_fit(data, y, classes)
            score = clf.score(data, y)
            assert_greater(score, 0.79)
            if average:
                assert_true(hasattr(clf, 'average_coef_'))
                assert_true(hasattr(clf, 'average_intercept_'))
                assert_true(hasattr(clf, 'standard_intercept_'))
                assert_true(hasattr(clf, 'standard_coef_'))


def test_classifier_refit():
    # Classifier can be retrained on different labels and features.
    clf = PassiveAggressiveClassifier(max_iter=5).fit(X, y)
    assert_array_equal(clf.classes_, np.unique(y))

    clf.fit(X[:, :-1], iris.target_names[y])
    assert_array_equal(clf.classes_, iris.target_names)


def test_classifier_correctness():
    """
    Tests the correctness of a custom Passive Aggressive classifier against the scikit-learn implementation.
    
    This function compares the coefficients of a custom Passive Aggressive classifier (`MyPassiveAggressive`) with the scikit-learn Passive Aggressive classifier (`PassiveAggressiveClassifier`) for different loss functions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `y_bin`: The binary target values, where non-1 values are converted to -1.
    - `loss`: The
    """

    y_bin = y.copy()
    y_bin[y != 1] = -1

    for loss in ("hinge", "squared_hinge"):

        clf1 = MyPassiveAggressive(
            C=1.0, loss=loss, fit_intercept=True, n_iter=2)
        clf1.fit(X, y_bin)

        for data in (X, X_csr):
            clf2 = PassiveAggressiveClassifier(
                C=1.0, loss=loss, fit_intercept=True, max_iter=2,
                shuffle=False, tol=None)
            clf2.fit(data, y_bin)

            assert_array_almost_equal(clf1.w, clf2.coef_.ravel(), decimal=2)


def test_classifier_undefined_methods():
    clf = PassiveAggressiveClassifier(max_iter=100)
    for meth in ("predict_proba", "predict_log_proba", "transform"):
        assert_raises(AttributeError, lambda x: getattr(clf, x), meth)


def test_class_weights():
    """
    Tests the effect of class weights on the PassiveAggressiveClassifier.
    
    This function evaluates the impact of different class weights on the
    classification of a new data point by the PassiveAggressiveClassifier.
    It demonstrates how adjusting class weights can alter the decision
    boundary and, consequently, the prediction of the classifier.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses a predefined dataset `X2` and labels `y2`.
    - It first trains a classifier without class
    """

    # Test class weights.
    X2 = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0],
                   [1.0, 1.0], [1.0, 0.0]])
    y2 = [1, 1, 1, -1, -1]

    clf = PassiveAggressiveClassifier(C=0.1, max_iter=100, class_weight=None,
                                      random_state=100)
    clf.fit(X2, y2)
    assert_array_equal(clf.predict([[0.2, -1.0]]), np.array([1]))

    # we give a small weights to class 1
    clf = PassiveAggressiveClassifier(C=0.1, max_iter=100,
                                      class_weight={1: 0.001},
                                      random_state=100)
    clf.fit(X2, y2)

    # now the hyperplane should rotate clock-wise and
    # the prediction on this point should shift
    assert_array_equal(clf.predict([[0.2, -1.0]]), np.array([-1]))


def test_partial_fit_weight_class_balanced():
    # partial_fit with class_weight='balanced' not supported
    clf = PassiveAggressiveClassifier(class_weight="balanced", max_iter=100)
    assert_raises(ValueError, clf.partial_fit, X, y, classes=np.unique(y))


def test_equal_class_weight():
    """
    Test that class_weight="balanced" has no effect on a balanced dataset.
    
    Parameters:
    - X2 (list of lists): The input features for the dataset.
    - y2 (list): The target labels for the dataset.
    
    This function checks the effect of the `class_weight` parameter on a balanced dataset. It fits a PassiveAggressiveClassifier with and without the "balanced" class weight and compares the resulting coefficients. The coefficients should be similar up to some epsilon due to the learning rate schedule.
    """

    X2 = [[1, 0], [1, 0], [0, 1], [0, 1]]
    y2 = [0, 0, 1, 1]
    clf = PassiveAggressiveClassifier(
        C=0.1, max_iter=1000, tol=None, class_weight=None)
    clf.fit(X2, y2)

    # Already balanced, so "balanced" weights should have no effect
    clf_balanced = PassiveAggressiveClassifier(
        C=0.1, max_iter=1000, tol=None, class_weight="balanced")
    clf_balanced.fit(X2, y2)

    clf_weighted = PassiveAggressiveClassifier(
        C=0.1, max_iter=1000, tol=None, class_weight={0: 0.5, 1: 0.5})
    clf_weighted.fit(X2, y2)

    # should be similar up to some epsilon due to learning rate schedule
    assert_almost_equal(clf.coef_, clf_weighted.coef_, decimal=2)
    assert_almost_equal(clf.coef_, clf_balanced.coef_, decimal=2)


def test_wrong_class_weight_label():
    # ValueError due to wrong class_weight label.
    X2 = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0],
                   [1.0, 1.0], [1.0, 0.0]])
    y2 = [1, 1, 1, -1, -1]

    clf = PassiveAggressiveClassifier(class_weight={0: 0.5}, max_iter=100)
    assert_raises(ValueError, clf.fit, X2, y2)


def test_wrong_class_weight_format():
    # ValueError due to wrong class_weight argument type.
    X2 = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0],
                   [1.0, 1.0], [1.0, 0.0]])
    y2 = [1, 1, 1, -1, -1]

    clf = PassiveAggressiveClassifier(class_weight=[0.5], max_iter=100)
    assert_raises(ValueError, clf.fit, X2, y2)

    clf = PassiveAggressiveClassifier(class_weight="the larch", max_iter=100)
    assert_raises(ValueError, clf.fit, X2, y2)


def test_regressor_mse():
    y_bin = y.copy()
    y_bin[y != 1] = -1

    for data in (X, X_csr):
        for fit_intercept in (True, False):
            for average in (False, True):
                reg = PassiveAggressiveRegressor(
                    C=1.0, fit_intercept=fit_intercept,
                    random_state=0, average=average, max_iter=5)
                reg.fit(data, y_bin)
                pred = reg.predict(data)
                assert_less(np.mean((pred - y_bin) ** 2), 1.7)
                if average:
                    assert_true(hasattr(reg, 'average_coef_'))
                    assert_true(hasattr(reg, 'average_intercept_'))
                    assert_true(hasattr(reg, 'standard_intercept_'))
                    assert_true(hasattr(reg, 'standard_coef_'))


def test_regressor_partial_fit():
    y_bin = y.copy()
    y_bin[y != 1] = -1

    for data in (X, X_csr):
        for average in (False, True):
            reg = PassiveAggressiveRegressor(
                C=1.0, fit_intercept=True, random_state=0,
                average=average, max_iter=100)
            for t in range(50):
                reg.partial_fit(data, y_bin)
            pred = reg.predict(data)
            assert_less(np.mean((pred - y_bin) ** 2), 1.7)
            if average:
                assert_true(hasattr(reg, 'average_coef_'))
                assert_true(hasattr(reg, 'average_intercept_'))
                assert_true(hasattr(reg, 'standard_intercept_'))
                assert_true(hasattr(reg, 'standard_coef_'))


def test_regressor_correctness():
    y_bin = y.copy()
    y_bin[y != 1] = -1

    for loss in ("epsilon_insensitive", "squared_epsilon_insensitive"):
        reg1 = MyPassiveAggressive(
            C=1.0, loss=loss, fit_intercept=True, n_iter=2)
        reg1.fit(X, y_bin)

        for data in (X, X_csr):
            reg2 = PassiveAggressiveRegressor(
                C=1.0, tol=None, loss=loss, fit_intercept=True, max_iter=2,
                shuffle=False)
            reg2.fit(data, y_bin)

            assert_array_almost_equal(reg1.w, reg2.coef_.ravel(), decimal=2)


def test_regressor_undefined_methods():
    reg = PassiveAggressiveRegressor(max_iter=100)
    for meth in ("transform",):
        assert_raises(AttributeError, lambda x: getattr(reg, x), meth)
