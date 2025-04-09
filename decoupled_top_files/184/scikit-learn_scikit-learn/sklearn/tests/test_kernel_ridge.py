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
    Test the equivalence of Ridge regression and linear Kernel Ridge regression.
    
    This function compares the predictions of a standard Ridge regression model
    with those of a linear Kernel Ridge regression model using the same alpha
    value. The `Ridge` function from scikit-learn is used to fit the model and
    predict values on the input data `X`. Similarly, the `KernelRidge` function
    with a linear kernel is employed for the comparison. The `assert_array_almost_equal`
    """

    pred = Ridge(alpha=1, fit_intercept=False).fit(X, y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csr():
    """
    Test the equivalence of Ridge regression and Kernel Ridge regression with a linear kernel.
    
    This function compares the predictions made by a Ridge regression model
    using the 'cholesky' solver and a Kernel Ridge regression model with a linear
    kernel on the same input data (Xcsr) and target variable (y).
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses the following important keywords and functions:
    - `Ridge`: A scikit
    """

    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsr, y).predict(Xcsr)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsr, y).predict(Xcsr)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_csc():
    """
    Test the equivalence of Ridge regression with linear kernel and KernelRidge.
    
    This function compares the predictions of Ridge regression with a linear
    kernel and KernelRidge. Both models are fitted on sparse matrix `Xcsc` using
    the same alpha value. The function asserts that the predictions from both
    models are almost equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `Ridge`: Performs linear least squares with l2 regularization.
    """

    pred = Ridge(alpha=1, fit_intercept=False,
                 solver="cholesky").fit(Xcsc, y).predict(Xcsc)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(Xcsc, y).predict(Xcsc)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_singular_kernel():
    """
    Test Kernel Ridge Regression with a singular kernel.
    
    This function evaluates the behavior of `KernelRidge` when using a linear
    kernel with an alpha value of 0. It compares the predictions made by a
    standard `Ridge` regression model with alpha=0 against those produced by
    `KernelRidge`. Specifically, it checks that both models produce nearly
    identical predictions despite the use of a singular kernel in `KernelRidge`.
    
    Parameters:
    None
    """

    # alpha=0 causes a LinAlgError in computing the dual coefficients,
    # which causes a fallback to a lstsq solver. This is tested here.
    pred = Ridge(alpha=0, fit_intercept=False).fit(X, y).predict(X)
    kr = KernelRidge(kernel="linear", alpha=0)
    ignore_warnings(kr.fit)(X, y)
    pred2 = kr.predict(X)
    assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_precomputed():
    """
    Test the performance of Kernel Ridge Regression with different kernels.
    
    This function evaluates the predictions made by `KernelRidge` using both
    the direct computation of the kernel matrix (`pairwise_kernels`) and the
    precomputed kernel matrix. It iterates over various kernel types including
    'linear', 'rbf', 'poly', and 'cosine'. For each kernel type, it computes
    the kernel matrix `K`, fits a `KernelRidge` model with the
    """

    for kernel in ["linear", "rbf", "poly", "cosine"]:
        K = pairwise_kernels(X, X, metric=kernel)
        pred = KernelRidge(kernel=kernel).fit(X, y).predict(X)
        pred2 = KernelRidge(kernel="precomputed").fit(K, y).predict(K)
        assert_array_almost_equal(pred, pred2)


def test_kernel_ridge_precomputed_kernel_unchanged():
    """
    Test that the precomputed kernel is unchanged after fitting a Kernel Ridge Regression model.
    
    This function verifies that the precomputed kernel matrix `K` remains unaltered
    after fitting a `KernelRidge` model with a precomputed kernel. The kernel matrix
    is initially copied to `K2` for comparison purposes. After fitting the model,
    the function asserts that `K` and `K2` are almost equal, indicating that the
    original kernel matrix was not modified
    """

    K = np.dot(X, X.T)
    K2 = K.copy()
    KernelRidge(kernel="precomputed").fit(K, y)
    assert_array_almost_equal(K, K2)


def test_kernel_ridge_sample_weights():
    """
    Test the usage of sample weights in Kernel Ridge Regression.
    
    This function evaluates the predictions made by a linear Ridge regression
    model and a Kernel Ridge regression model with a linear kernel and a
    precomputed kernel, using sample weights. The sample weights are randomly
    generated for each sample in the dataset.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `np.dot`: Computes the dot product between the input features and their
    transposed version
    """

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
    """
    Tests the Kernel Ridge Regression model with multi-output data.
    
    This function compares the predictions of a standard Ridge regression model
    and a Kernel Ridge regression model using a linear kernel on multi-output
    data. It ensures that both models produce nearly identical results.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `Ridge`: A linear regression model with L2 regularization.
    - `KernelRidge`: A non-linear regression model using a specified kernel.
    """

    pred = Ridge(alpha=1, fit_intercept=False).fit(X, Y).predict(X)
    pred2 = KernelRidge(kernel="linear", alpha=1).fit(X, Y).predict(X)
    assert_array_almost_equal(pred, pred2)

    pred3 = KernelRidge(kernel="linear", alpha=1).fit(X, y).predict(X)
    pred3 = np.array([pred3, pred3]).T
    assert_array_almost_equal(pred2, pred3)
