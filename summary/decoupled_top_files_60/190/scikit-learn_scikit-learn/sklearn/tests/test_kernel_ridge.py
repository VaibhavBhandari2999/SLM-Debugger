import numpy as np
import scipy.sparse as sp

from sklearn.datasets import make_regression
from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.utils.testing import ignore_warnings

from sklearn.utils.testing import assert_array_almost_equal


X, y = make_regression(n_features=10, random_state=0)
Xcsr = sp.csr_matrix(X)
Xcsc = sp.csc_matrix(X)
Y = np.array([y, y]).T


def test_kernel_ridge():
    """
    Test that the linear kernel of KernelRidge is equivalent to Ridge.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    X (numpy.ndarray): Input data.
    y (numpy.ndarray): Target values.
    """

    pred = Ridge(alpha=1, fit_intercept=False).fit(X, y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csr():
    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsr, y).predict(Xcsr)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsr, y).predict(Xcsr)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csc():
    """
    Test the equivalence between Ridge regression and Kernel Ridge regression with a linear kernel.
    
    Parameters:
    Xcsc (scipy.sparse.csc_matrix): The input feature matrix in Compressed Sparse Column format.
    y (array-like): The target values.
    
    Returns:
    None: This function asserts the almost equal predictions from Ridge regression and Kernel Ridge regression with a linear kernel. It does not return any value but raises an AssertionError if the predictions are not almost equal.
    """

    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsc, y).predict(Xcsc)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsc, y).predict(Xcsc)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_singular_kernel():
    """
    Test Kernel Ridge Regression with a singular kernel.
    
    This function checks the behavior of the Kernel Ridge Regression model when
    the kernel matrix is singular, which can cause issues in computing the dual
    coefficients. Specifically, it tests the model's ability to handle such cases
    by comparing predictions made with a direct Ridge regression model and a
    Kernel Ridge Regression model that falls back to a least squares solver.
    
    Parameters:
    X : array-like, shape (n_samples, n_features)
    Training data.
    """

    # alpha=0 causes a LinAlgError in computing the dual coefficients,
    # which causes a fallback to a lstsq solver. This is tested here.
    pred = Ridge(alpha=0, fit_intercept=False).fit(X, y).predict(X)
    kr = KernelRidge(kernel="linear", alpha=0)
    ignore_warnings(kr.fit)(X, y)
    pred2 = kr.predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_precomputed():
    for kernel in ["linear", "rbf", "poly", "cosine"]:
        K = pairwise_kernels(X, X, metric=kernel)
        pred = KernelRidge(kernel=kernel).fit(X, y).predict(X)
        pred2 = KernelRidge(kernel="precomputed").fit(K, y).predict(K)
        assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_precomputed_kernel_unchanged():
    """
    Test that the precomputed kernel is not modified by KernelRidge.
    
    Parameters:
    X (array-like): Input data for kernel computation.
    y (array-like): Target values for fitting the model.
    
    This function checks that the precomputed kernel matrix `K` remains unchanged
    after fitting a KernelRidge model with the 'precomputed' kernel. A copy of the
    original kernel matrix `K2` is made before fitting the model, and the function
    asserts that the original and
    """

    K = np.dot(X, X.T)
    K2 = K.copy()
    KernelRidge(kernel="precomputed").fit(K, y)
    assert_array_almost_equal(K, K2)


def test_kernel_ridge_sample_weights():
    K = np.dot(X, X.T)  # precomputed kernel
    sw = np.random.RandomState(0).rand(X.shape[0])

    pred = Ridge(alpha=1,
                 fit_intercept=False).fit(X, y, sample_weight=sw).predict(X)
    pred2 = KernelRidge(kernel="linear",
                        alpha=1).fit(X, y, sample_weight=sw).predict(X)
    pred3 = KernelRidge(kernel="precomputed",
                        alpha=1).fit(K, y, sample_weight=sw).predict(K)
    assert_array_almost_equal(pred, pred2)
    assert_array_almost_equal(pred, pred3)


def test_kernel_ridge_multi_output():
    pred = Ridge(alpha=1, fit_intercept=False).fit(X, Y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, Y).predict(X)
    assert_array_almost_equal(pred, pred2)

    pred3 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    pred3 = np.array([pred3, pred3]).T
    assert_array_almost_equal(pred2, pred3)
red2, pred3)
