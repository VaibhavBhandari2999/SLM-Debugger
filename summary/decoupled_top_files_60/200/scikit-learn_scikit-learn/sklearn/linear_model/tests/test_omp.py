# Author: Vlad Niculae
# License: BSD 3 clause

import numpy as np

from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_warns
from sklearn.utils.testing import ignore_warnings


from sklearn.linear_model import (orthogonal_mp, orthogonal_mp_gram,
                                  OrthogonalMatchingPursuit,
                                  OrthogonalMatchingPursuitCV,
                                  LinearRegression)
from sklearn.utils import check_random_state
from sklearn.datasets import make_sparse_coded_signal

n_samples, n_features, n_nonzero_coefs, n_targets = 25, 35, 5, 3
y, X, gamma = make_sparse_coded_signal(n_targets, n_features, n_samples,
                                       n_nonzero_coefs, random_state=0)
# Make X not of norm 1 for testing
X *= 10
y *= 10
G, Xy = np.dot(X.T, X), np.dot(X.T, y)
# this makes X (n_samples, n_features)
# and y (n_samples, 3)


def test_correct_shapes():
    """
    Test the correctness of the shapes returned by the orthogonal_mp function.
    
    This function checks that the output of the orthogonal_mp function has the expected shape for both single and multi-output cases.
    
    Parameters:
    X (array-like): The input data matrix.
    y (array-like): The target data, which can be either a single output or multi-output.
    
    Returns:
    None: This function asserts the correctness of the output shapes and will raise an AssertionError if the shapes do not match the expected results.
    """

    assert (orthogonal_mp(X, y[:, 0], n_nonzero_coefs=5).shape ==
                 (n_features,))
    assert (orthogonal_mp(X, y, n_nonzero_coefs=5).shape ==
                 (n_features, 3))


def test_correct_shapes_gram():
    assert (orthogonal_mp_gram(G, Xy[:, 0], n_nonzero_coefs=5).shape ==
                 (n_features,))
    assert (orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5).shape ==
                 (n_features, 3))


def test_n_nonzero_coefs():
    assert np.count_nonzero(orthogonal_mp(X, y[:, 0], n_nonzero_coefs=5)) <= 5
    assert np.count_nonzero(orthogonal_mp(X, y[:, 0],
                                          n_nonzero_coefs=5,
                                          precompute=True)) <= 5


def test_tol():
    """
    Tests the orthogonal matching pursuit algorithm with a specified tolerance.
    
    Parameters:
    tol (float): The tolerance value for the algorithm.
    
    Returns:
    None: This function does not return any value. It asserts that the squared error of the reconstructed signal using the algorithm is within the specified tolerance.
    """

    tol = 0.5
    gamma = orthogonal_mp(X, y[:, 0], tol=tol)
    gamma_gram = orthogonal_mp(X, y[:, 0], tol=tol, precompute=True)
    assert np.sum((y[:, 0] - np.dot(X, gamma)) ** 2) <= tol
    assert np.sum((y[:, 0] - np.dot(X, gamma_gram)) ** 2) <= tol


def test_with_without_gram():
    assert_array_almost_equal(
        orthogonal_mp(X, y, n_nonzero_coefs=5),
        orthogonal_mp(X, y, n_nonzero_coefs=5, precompute=True))


def test_with_without_gram_tol():
    assert_array_almost_equal(
        orthogonal_mp(X, y, tol=1.),
        orthogonal_mp(X, y, tol=1., precompute=True))


def test_unreachable_accuracy():
    """
    Test the accuracy of the orthogonal matching pursuit algorithm.
    
    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
    The input data matrix.
    
    y : array-like, shape (n_samples,)
    The target values.
    
    tol : float, optional
    The tolerance for the stopping condition of the algorithm. If `tol` is
    not provided, the algorithm will use the number of features as the
    stopping condition.
    
    Returns
    -------
    result : array-like, shape (n
    """

    assert_array_almost_equal(
        orthogonal_mp(X, y, tol=0),
        orthogonal_mp(X, y, n_nonzero_coefs=n_features))

    assert_array_almost_equal(
        assert_warns(RuntimeWarning, orthogonal_mp, X, y, tol=0,
                     precompute=True),
        orthogonal_mp(X, y, precompute=True,
                      n_nonzero_coefs=n_features))


def test_bad_input():
    assert_raises(ValueError, orthogonal_mp, X, y, tol=-1)
    assert_raises(ValueError, orthogonal_mp, X, y, n_nonzero_coefs=-1)
    assert_raises(ValueError, orthogonal_mp, X, y,
                  n_nonzero_coefs=n_features + 1)
    assert_raises(ValueError, orthogonal_mp_gram, G, Xy, tol=-1)
    assert_raises(ValueError, orthogonal_mp_gram, G, Xy, n_nonzero_coefs=-1)
    assert_raises(ValueError, orthogonal_mp_gram, G, Xy,
                  n_nonzero_coefs=n_features + 1)


def test_perfect_signal_recovery():
    idx, = gamma[:, 0].nonzero()
    gamma_rec = orthogonal_mp(X, y[:, 0], 5)
    gamma_gram = orthogonal_mp_gram(G, Xy[:, 0], 5)
    assert_array_equal(idx, np.flatnonzero(gamma_rec))
    assert_array_equal(idx, np.flatnonzero(gamma_gram))
    assert_array_almost_equal(gamma[:, 0], gamma_rec, decimal=2)
    assert_array_almost_equal(gamma[:, 0], gamma_gram, decimal=2)


def test_orthogonal_mp_gram_readonly():
    """
    Test the orthogonal_mp_gram function with a readonly array.
    
    This function ensures that the orthogonal_mp_gram function works correctly
    even when the input arrays are marked as readonly. Specifically, it tests
    the function with a copy of the input array that has been marked as readonly
    and checks that the function still returns the expected results.
    
    Parameters
    ----------
    G : array-like
    The Gram matrix used in the orthogonal matching pursuit.
    Xy : array-like
    The target vector or matrix used in
    """

    # Non-regression test for:
    # https://github.com/scikit-learn/scikit-learn/issues/5956
    idx, = gamma[:, 0].nonzero()
    G_readonly = G.copy()
    G_readonly.setflags(write=False)
    Xy_readonly = Xy.copy()
    Xy_readonly.setflags(write=False)
    gamma_gram = orthogonal_mp_gram(G_readonly, Xy_readonly[:, 0], 5,
                                    copy_Gram=False, copy_Xy=False)
    assert_array_equal(idx, np.flatnonzero(gamma_gram))
    assert_array_almost_equal(gamma[:, 0], gamma_gram, decimal=2)


def test_estimator():
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=n_nonzero_coefs)
    omp.fit(X, y[:, 0])
    assert omp.coef_.shape == (n_features,)
    assert omp.intercept_.shape == ()
    assert np.count_nonzero(omp.coef_) <= n_nonzero_coefs

    omp.fit(X, y)
    assert omp.coef_.shape == (n_targets, n_features)
    assert omp.intercept_.shape == (n_targets,)
    assert np.count_nonzero(omp.coef_) <= n_targets * n_nonzero_coefs

    coef_normalized = omp.coef_[0].copy()
    omp.set_params(fit_intercept=True, normalize=False)
    omp.fit(X, y[:, 0])
    assert_array_almost_equal(coef_normalized, omp.coef_)

    omp.set_params(fit_intercept=False, normalize=False)
    omp.fit(X, y[:, 0])
    assert np.count_nonzero(omp.coef_) <= n_nonzero_coefs
    assert omp.coef_.shape == (n_features,)
    assert omp.intercept_ == 0

    omp.fit(X, y)
    assert omp.coef_.shape == (n_targets, n_features)
    assert omp.intercept_ == 0
    assert np.count_nonzero(omp.coef_) <= n_targets * n_nonzero_coefs


def test_identical_regressors():
    """
    Test the behavior of orthogonal_mp when identical regressors are present.
    
    This function creates a copy of the input matrix `X`, duplicates one of the
    columns, and then attempts to perform orthogonal matching pursuit (OMP) on
    the modified matrix. The expected behavior is to raise a RuntimeWarning due
    to the presence of identical regressors.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    RuntimeWarning: If the OMP algorithm does not raise a warning when
    identical regressors
    """

    newX = X.copy()
    newX[:, 1] = newX[:, 0]
    gamma = np.zeros(n_features)
    gamma[0] = gamma[1] = 1.
    newy = np.dot(newX, gamma)
    assert_warns(RuntimeWarning, orthogonal_mp, newX, newy, 2)


def test_swapped_regressors():
    """
    Tests the behavior of the orthogonal matching pursuit (OMP) algorithm when the regressors in the design matrix X are swapped.
    
    Parameters:
    X (numpy.ndarray): The design matrix with shape (n_samples, n_features).
    n_features (int): The number of features in the design matrix X.
    G (numpy.ndarray): Gram matrix of X, used for the Gram matrix version of OMP.
    new_y (numpy.ndarray): The target vector after applying the regressor weights gamma to X
    """

    gamma = np.zeros(n_features)
    # X[:, 21] should be selected first, then X[:, 0] selected second,
    # which will take X[:, 21]'s place in case the algorithm does
    # column swapping for optimization (which is the case at the moment)
    gamma[21] = 1.0
    gamma[0] = 0.5
    new_y = np.dot(X, gamma)
    new_Xy = np.dot(X.T, new_y)
    gamma_hat = orthogonal_mp(X, new_y, 2)
    gamma_hat_gram = orthogonal_mp_gram(G, new_Xy, 2)
    assert_array_equal(np.flatnonzero(gamma_hat), [0, 21])
    assert_array_equal(np.flatnonzero(gamma_hat_gram), [0, 21])


def test_no_atoms():
    y_empty = np.zeros_like(y)
    Xy_empty = np.dot(X.T, y_empty)
    gamma_empty = ignore_warnings(orthogonal_mp)(X, y_empty, 1)
    gamma_empty_gram = ignore_warnings(orthogonal_mp)(G, Xy_empty, 1)
    assert np.all(gamma_empty == 0)
    assert np.all(gamma_empty_gram == 0)


def test_omp_path():
    path = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=True)
    last = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=False)
    assert path.shape == (n_features, n_targets, 5)
    assert_array_almost_equal(path[:, :, -1], last)
    path = orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5, return_path=True)
    last = orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5, return_path=False)
    assert path.shape == (n_features, n_targets, 5)
    assert_array_almost_equal(path[:, :, -1], last)


def test_omp_return_path_prop_with_gram():
    """
    Return the solution path using Orthogonal Matching Pursuit (OMP) with Gram matrix precomputation.
    
    This function computes the OMP solution path for a given input matrix `X` and target vector `y`. The path is computed for a specified number of non-zero coefficients (`n_nonzero_coefs`) and with or without returning the full path.
    
    Parameters:
    X (array-like): Input data matrix.
    y (array-like): Target vector.
    n_nonzero_coefs (int):
    """

    path = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=True,
                         precompute=True)
    last = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=False,
                         precompute=True)
    assert path.shape == (n_features, n_targets, 5)
    assert_array_almost_equal(path[:, :, -1], last)


def test_omp_cv():
    y_ = y[:, 0]
    gamma_ = gamma[:, 0]
    ompcv = OrthogonalMatchingPursuitCV(normalize=True, fit_intercept=False,
                                        max_iter=10)
    ompcv.fit(X, y_)
    assert ompcv.n_nonzero_coefs_ == n_nonzero_coefs
    assert_array_almost_equal(ompcv.coef_, gamma_)
    omp = OrthogonalMatchingPursuit(normalize=True, fit_intercept=False,
                                    n_nonzero_coefs=ompcv.n_nonzero_coefs_)
    omp.fit(X, y_)
    assert_array_almost_equal(ompcv.coef_, omp.coef_)


def test_omp_reaches_least_squares():
    """
    Test that OMP reaches the least squares solution.
    
    This function checks that the Orthogonal Matching Pursuit (OMP) algorithm
    reaches the least squares solution when the number of non-zero coefficients
    is equal to the number of features. It uses a small, simple dataset for
    sanity checking, as OMP may stop early if it finds a solution with fewer
    non-zero coefficients.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses a random dataset with
    """

    # Use small simple data; it's a sanity check but OMP can stop early
    rng = check_random_state(0)
    n_samples, n_features = (10, 8)
    n_targets = 3
    X = rng.randn(n_samples, n_features)
    Y = rng.randn(n_samples, n_targets)
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=n_features)
    lstsq = LinearRegression()
    omp.fit(X, Y)
    lstsq.fit(X, Y)
    assert_array_almost_equal(omp.coef_, lstsq.coef_)
