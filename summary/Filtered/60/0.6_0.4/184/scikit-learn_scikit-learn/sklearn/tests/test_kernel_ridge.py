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
    pred = Ridge(alpha=1, fit_intercept=False).fit(X, y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csr():
    """
    Test the equivalence of Ridge regression and Kernel Ridge regression with a linear kernel.
    
    This function compares the predictions of a Ridge regression model with the predictions of a Kernel Ridge regression model using a linear kernel. Both models are fitted on a sparse CSR matrix `Xcsr` and the target variable `y`. The function asserts that the predictions from both models are almost equal, indicating that the linear kernel in Kernel Ridge regression is equivalent to Ridge regression.
    
    Parameters:
    Xcsr (csr_matrix): A sparse CSR matrix
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
    """
    Test the KernelRidge with precomputed kernel.
    
    This function evaluates the performance of the KernelRidge regressor when
    using precomputed kernel matrices for different kernel types: 'linear',
    'rbf', 'poly', and 'cosine'. It computes the kernel matrix using
    pairwise_kernels and then fits and predicts using both the direct kernel
    regression and the precomputed kernel regression. The results from both
    methods are compared to ensure they are almost equal.
    
    Parameters:
    None
    """

    for kernel in ["linear", "rbf", "poly", "cosine"]:
        K = pairwise_kernels(X, X, metric=kernel)
        pred = KernelRidge(kernel=kernel).fit(X, y).predict(X)
        pred2 = KernelRidge(kernel="precomputed").fit(K, y).predict(K)
        assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_precomputed_kernel_unchanged():
    """
    Test that the precomputed kernel is not modified by the KernelRidge estimator.
    
    Parameters:
    X (array-like): Input data for kernel computation.
    y (array-like): Target values for fitting the model.
    
    This function checks that the precomputed kernel matrix `K` remains unchanged after fitting a KernelRidge model with the 'precomputed' kernel. It creates a copy of the kernel matrix `K2` before fitting and then compares it with the original `K` after fitting the model
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
