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
    Test Kernel Ridge Regression against a linear Ridge Regression.
    
    This function compares the predictions of a linear Ridge Regression model
    with an alpha of 1 and no intercept, against a Kernel Ridge Regression model
    with the same parameters and a linear kernel. The function asserts that the
    predictions from both models are almost equal, indicating that the Kernel
    Ridge Regression with a linear kernel behaves similarly to a linear Ridge
    Regression.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    X : array-like
    """

    pred = Ridge(alpha=1, fit_intercept=False).fit(X, y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csr():
    """
    Tests the equivalence of Ridge regression and Kernel Ridge regression with a linear kernel.
    
    This function compares the predictions of a Ridge regression model and a Kernel Ridge regression model with a linear kernel on the same input data (Xcsr) and target variable (y). Both models are fitted with the same alpha value and no intercept term. The function asserts that the predictions from both models are almost equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    Xcsr (scipy.sparse.csr_matrix):
    """

    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsr, y).predict(Xcsr)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsr, y).predict(Xcsr)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csc():
    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsc, y).predict(Xcsc)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsc, y).predict(Xcsc)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_singular_kernel():
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
