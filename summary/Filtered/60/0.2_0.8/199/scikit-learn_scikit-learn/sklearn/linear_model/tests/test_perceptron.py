import numpy as np
import scipy.sparse as sp
import pytest

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_raises

from sklearn.utils import check_random_state
from sklearn.datasets import load_iris
from sklearn.linear_model import Perceptron

iris = load_iris()
random_state = check_random_state(12)
indices = np.arange(iris.data.shape[0])
random_state.shuffle(indices)
X = iris.data[indices]
y = iris.target[indices]
X_csr = sp.csr_matrix(X)
X_csr.sort_indices()


class MyPerceptron:

    def __init__(self, n_iter=1):
        self.n_iter = n_iter

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features, dtype=np.float64)
        self.b = 0.0

        for t in range(self.n_iter):
            for i in range(n_samples):
                if self.predict(X[i])[0] != y[i]:
                    self.w += y[i] * X[i]
                    self.b += y[i]

    def project(self, X):
        return np.dot(X, self.w) + self.b

    def predict(self, X):
        X = np.atleast_2d(X)
        return np.sign(self.project(X))


# 0.23. warning about tol not having its correct default value.
@pytest.mark.filterwarnings('ignore:max_iter and tol parameters have been')
def test_perceptron_accuracy():
    """
    Tests the accuracy of a Perceptron classifier on given data.
    
    This function iterates over a list of datasets (X, X_csr) and trains a Perceptron classifier on each dataset. The classifier is configured with the following parameters:
    - max_iter: 100 (maximum number of passes over the training dataset)
    - tol: None (tolerance for stopping criterion)
    - shuffle: False (whether to shuffle the data before each epoch)
    
    For each dataset, the function fits
    """

    for data in (X, X_csr):
        clf = Perceptron(max_iter=100, tol=None, shuffle=False)
        clf.fit(data, y)
        score = clf.score(data, y)
        assert score > 0.7


# 0.23. warning about tol not having its correct default value.
@pytest.mark.filterwarnings('ignore:max_iter and tol parameters have been')
def test_perceptron_correctness():
    y_bin = y.copy()
    y_bin[y != 1] = -1

    clf1 = MyPerceptron(n_iter=2)
    clf1.fit(X, y_bin)

    clf2 = Perceptron(max_iter=2, shuffle=False, tol=None)
    clf2.fit(X, y_bin)

    assert_array_almost_equal(clf1.w, clf2.coef_.ravel())


def test_undefined_methods():
    """
    Tests for undefined methods in the Perceptron class.
    
    This function checks for the presence of undefined methods in the Perceptron class. It creates an instance of the Perceptron class with a specified maximum number of iterations. Then, it iterates over a list of method names and uses the `assert_raises` function to verify that attempting to access these methods raises an `AttributeError`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AttributeError: If any of the specified methods are
    """

    clf = Perceptron(max_iter=100)
    for meth in ("predict_proba", "predict_log_proba"):
        assert_raises(AttributeError, lambda x: getattr(clf, x), meth)
