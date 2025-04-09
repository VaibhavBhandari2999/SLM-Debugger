import numpy as np
from scipy.sparse import csr_matrix
import pytest

from sklearn.utils.testing import assert_array_equal, assert_equal
from sklearn.utils.testing import assert_not_equal
from sklearn.utils.testing import assert_array_almost_equal, assert_raises
from sklearn.utils.testing import assert_less_equal

from sklearn.metrics.pairwise import kernel_metrics
from sklearn.kernel_approximation import RBFSampler
from sklearn.kernel_approximation import AdditiveChi2Sampler
from sklearn.kernel_approximation import SkewedChi2Sampler
from sklearn.kernel_approximation import Nystroem
from sklearn.metrics.pairwise import polynomial_kernel, rbf_kernel, chi2_kernel

# generate data
rng = np.random.RandomState(0)
X = rng.random_sample(size=(300, 50))
Y = rng.random_sample(size=(300, 50))
X /= X.sum(axis=1)[:, np.newaxis]
Y /= Y.sum(axis=1)[:, np.newaxis]


def test_additive_chi2_sampler():
    """
    Test the AdditiveChi2Sampler for approximating a kernel on random data.
    
    This function tests whether the AdditiveChi2Sampler can accurately approximate
    a kernel matrix given two sets of input data `X` and `Y`. The function computes
    the exact kernel using the provided formula and then uses the AdditiveChi2Sampler
    to approximate this kernel. It compares the exact kernel with the approximated
    one and ensures they are almost equal within a certain tolerance level.
    """

    # test that AdditiveChi2Sampler approximates kernel on random data

    # compute exact kernel
    # abbreviations for easier formula
    X_ = X[:, np.newaxis, :]
    Y_ = Y[np.newaxis, :, :]

    large_kernel = 2 * X_ * Y_ / (X_ + Y_)

    # reduce to n_samples_x x n_samples_y by summing over features
    kernel = (large_kernel.sum(axis=2))

    # approximate kernel mapping
    transform = AdditiveChi2Sampler(sample_steps=3)
    X_trans = transform.fit_transform(X)
    Y_trans = transform.transform(Y)

    kernel_approx = np.dot(X_trans, Y_trans.T)

    assert_array_almost_equal(kernel, kernel_approx, 1)

    X_sp_trans = transform.fit_transform(csr_matrix(X))
    Y_sp_trans = transform.transform(csr_matrix(Y))

    assert_array_equal(X_trans, X_sp_trans.A)
    assert_array_equal(Y_trans, Y_sp_trans.A)

    # test error is raised on negative input
    Y_neg = Y.copy()
    Y_neg[0, 0] = -1
    assert_raises(ValueError, transform.transform, Y_neg)

    # test error on invalid sample_steps
    transform = AdditiveChi2Sampler(sample_steps=4)
    assert_raises(ValueError, transform.fit, X)

    # test that the sample interval is set correctly
    sample_steps_available = [1, 2, 3]
    for sample_steps in sample_steps_available:

        # test that the sample_interval is initialized correctly
        transform = AdditiveChi2Sampler(sample_steps=sample_steps)
        assert_equal(transform.sample_interval, None)

        # test that the sample_interval is changed in the fit method
        transform.fit(X)
        assert_not_equal(transform.sample_interval_, None)

    # test that the sample_interval is set correctly
    sample_interval = 0.3
    transform = AdditiveChi2Sampler(sample_steps=4,
                                    sample_interval=sample_interval)
    assert_equal(transform.sample_interval, sample_interval)
    transform.fit(X)
    assert_equal(transform.sample_interval_, sample_interval)


def test_skewed_chi2_sampler():
    """
    Tests the SkewedChi2Sampler for approximating the kernel on random data.
    
    This function evaluates the exact kernel between two sets of samples `X` and `Y`
    using the skewed chi-squared kernel. It then uses the SkewedChi2Sampler to
    approximate the same kernel and compares the results. The function also checks
    if the approximated kernel matches the exact one within a certain tolerance level.
    
    Parameters:
    None (the function uses predefined data).
    
    Returns
    """

    # test that RBFSampler approximates kernel on random data

    # compute exact kernel
    c = 0.03
    # set on negative component but greater than c to ensure that the kernel
    # approximation is valid on the group (-c; +\infty) endowed with the skewed
    # multiplication.
    Y[0, 0] = -c / 2.

    # abbreviations for easier formula
    X_c = (X + c)[:, np.newaxis, :]
    Y_c = (Y + c)[np.newaxis, :, :]

    # we do it in log-space in the hope that it's more stable
    # this array is n_samples_x x n_samples_y big x n_features
    log_kernel = ((np.log(X_c) / 2.) + (np.log(Y_c) / 2.) + np.log(2.) -
                  np.log(X_c + Y_c))
    # reduce to n_samples_x x n_samples_y by summing over features in log-space
    kernel = np.exp(log_kernel.sum(axis=2))

    # approximate kernel mapping
    transform = SkewedChi2Sampler(skewedness=c, n_components=1000,
                                  random_state=42)
    X_trans = transform.fit_transform(X)
    Y_trans = transform.transform(Y)

    kernel_approx = np.dot(X_trans, Y_trans.T)
    assert_array_almost_equal(kernel, kernel_approx, 1)
    assert np.isfinite(kernel).all(), \
        'NaNs found in the Gram matrix'
    assert np.isfinite(kernel_approx).all(), \
        'NaNs found in the approximate Gram matrix'

    # test error is raised on when inputs contains values smaller than -c
    Y_neg = Y.copy()
    Y_neg[0, 0] = -c * 2.
    assert_raises(ValueError, transform.transform, Y_neg)


def test_rbf_sampler():
    """
    Test the RBFSampler class by comparing the exact RBF kernel with its approximation.
    
    This function evaluates the performance of the RBFSampler by computing the RBF kernel
    between two sets of data points (X and Y) using both the exact method and the approximate
    method via RBFSampler. The key steps include:
    
    1. Compute the exact RBF kernel using `rbf_kernel`.
    2. Approximate the RBF kernel using `RBFSampler`
    """

    # test that RBFSampler approximates kernel on random data
    # compute exact kernel
    gamma = 10.
    kernel = rbf_kernel(X, Y, gamma=gamma)

    # approximate kernel mapping
    rbf_transform = RBFSampler(gamma=gamma, n_components=1000, random_state=42)
    X_trans = rbf_transform.fit_transform(X)
    Y_trans = rbf_transform.transform(Y)
    kernel_approx = np.dot(X_trans, Y_trans.T)

    error = kernel - kernel_approx
    assert_less_equal(np.abs(np.mean(error)), 0.01)  # close to unbiased
    np.abs(error, out=error)
    assert_less_equal(np.max(error), 0.1)  # nothing too far off
    assert_less_equal(np.mean(error), 0.05)  # mean is fairly close


def test_input_validation():
    """
    Test input validation for kernel approximation transformers.
    
    This function verifies that kernel approximation transformers can handle both
    list inputs and sparse matrix inputs. It checks the functionality of three
    specific transformers: `AdditiveChi2Sampler`, `SkewedChi2Sampler`, and
    `RBFSampler`. The transformers are expected to fit and transform the input
    data correctly regardless of its format.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `Add
    """

    # Regression test: kernel approx. transformers should work on lists
    # No assertions; the old versions would simply crash
    X = [[1, 2], [3, 4], [5, 6]]
    AdditiveChi2Sampler().fit(X).transform(X)
    SkewedChi2Sampler().fit(X).transform(X)
    RBFSampler().fit(X).transform(X)

    X = csr_matrix(X)
    RBFSampler().fit(X).transform(X)


def test_nystroem_approximation():
    """
    Test the Nystroem approximation method.
    
    This function evaluates the Nystroem approximation method by performing
    several tests on a randomly generated dataset. The tests include:
    
    - Verifying the exactness of the approximation when `n_components` equals
    the number of samples.
    - Checking the shape of the transformed data after applying the
    Nystroem transformation with a specified number of components.
    - Testing the functionality with a custom linear kernel.
    - Ensuring
    """

    # some basic tests
    rnd = np.random.RandomState(0)
    X = rnd.uniform(size=(10, 4))

    # With n_components = n_samples this is exact
    X_transformed = Nystroem(n_components=X.shape[0]).fit_transform(X)
    K = rbf_kernel(X)
    assert_array_almost_equal(np.dot(X_transformed, X_transformed.T), K)

    trans = Nystroem(n_components=2, random_state=rnd)
    X_transformed = trans.fit(X).transform(X)
    assert_equal(X_transformed.shape, (X.shape[0], 2))

    # test callable kernel
    def linear_kernel(X, Y):
        return np.dot(X, Y.T)
    trans = Nystroem(n_components=2, kernel=linear_kernel, random_state=rnd)
    X_transformed = trans.fit(X).transform(X)
    assert_equal(X_transformed.shape, (X.shape[0], 2))

    # test that available kernels fit and transform
    kernels_available = kernel_metrics()
    for kern in kernels_available:
        trans = Nystroem(n_components=2, kernel=kern, random_state=rnd)
        X_transformed = trans.fit(X).transform(X)
        assert_equal(X_transformed.shape, (X.shape[0], 2))


def test_nystroem_default_parameters():
    """
    Test the default parameters of the Nystroem transformer.
    
    This function evaluates the behavior of the Nystroem transformer with
    different kernels (rbf and chi2) using default parameters. It checks if the
    transformed data matches the expected kernel matrices for both kernels.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `Nystroem`: The transformer used to approximate the feature map of a kernel.
    - `rbf_kernel
    """

    rnd = np.random.RandomState(42)
    X = rnd.uniform(size=(10, 4))

    # rbf kernel should behave as gamma=None by default
    # aka gamma = 1 / n_features
    nystroem = Nystroem(n_components=10)
    X_transformed = nystroem.fit_transform(X)
    K = rbf_kernel(X, gamma=None)
    K2 = np.dot(X_transformed, X_transformed.T)
    assert_array_almost_equal(K, K2)

    # chi2 kernel should behave as gamma=1 by default
    nystroem = Nystroem(kernel='chi2', n_components=10)
    X_transformed = nystroem.fit_transform(X)
    K = chi2_kernel(X, gamma=1)
    K2 = np.dot(X_transformed, X_transformed.T)
    assert_array_almost_equal(K, K2)


def test_nystroem_singular_kernel():
    """
    Test the Nystroem method with a singular kernel matrix.
    
    This function evaluates the Nystroem method's performance on a dataset
    with duplicated samples using a Radial Basis Function (RBF) kernel. The
    function generates a random dataset `X` and applies the Nystroem method
    with a specified gamma value. It then compares the transformed data with
    the original RBF kernel matrix to ensure they are approximately equal.
    
    Parameters:
    None
    """

    # test that nystroem works with singular kernel matrix
    rng = np.random.RandomState(0)
    X = rng.rand(10, 20)
    X = np.vstack([X] * 2)  # duplicate samples

    gamma = 100
    N = Nystroem(gamma=gamma, n_components=X.shape[0]).fit(X)
    X_transformed = N.transform(X)

    K = rbf_kernel(X, gamma=gamma)

    assert_array_almost_equal(K, np.dot(X_transformed, X_transformed.T))
    assert np.all(np.isfinite(Y))


def test_nystroem_poly_kernel_params():
    """
    Test that Nystroem transformer can handle parameters besides gamma.
    
    This function verifies that the Nystroem transformer from scikit-learn
    can correctly handle additional kernel parameters such as `degree` and
    `coef0`. It uses a random state to generate a dataset and computes a
    polynomial kernel matrix using the `polynomial_kernel` function. The
    Nystroem transformer is then fitted and transformed on the dataset,
    and the resulting transformed data is compared
    """

    # Non-regression: Nystroem should pass other parameters beside gamma.
    rnd = np.random.RandomState(37)
    X = rnd.uniform(size=(10, 4))

    K = polynomial_kernel(X, degree=3.1, coef0=.1)
    nystroem = Nystroem(kernel="polynomial", n_components=X.shape[0],
                        degree=3.1, coef0=.1)
    X_transformed = nystroem.fit_transform(X)
    assert_array_almost_equal(np.dot(X_transformed, X_transformed.T), K)


def test_nystroem_callable():
    """
    Histogram kernel that writes to a log.
    """

    # Test Nystroem on a callable.
    rnd = np.random.RandomState(42)
    n_samples = 10
    X = rnd.uniform(size=(n_samples, 4))

    def logging_histogram_kernel(x, y, log):
        """Histogram kernel that writes to a log."""
        log.append(1)
        return np.minimum(x, y).sum()

    kernel_log = []
    X = list(X)     # test input validation
    Nystroem(kernel=logging_histogram_kernel,
             n_components=(n_samples - 1),
             kernel_params={'log': kernel_log}).fit(X)
    assert_equal(len(kernel_log), n_samples * (n_samples - 1) / 2)

    def linear_kernel(X, Y):
        return np.dot(X, Y.T)

    # if degree, gamma or coef0 is passed, we raise a warning
    msg = "Don't pass gamma, coef0 or degree to Nystroem"
    params = ({'gamma': 1}, {'coef0': 1}, {'degree': 2})
    for param in params:
        ny = Nystroem(kernel=linear_kernel, **param)
        with pytest.raises(ValueError, match=msg):
            ny.fit(X)
