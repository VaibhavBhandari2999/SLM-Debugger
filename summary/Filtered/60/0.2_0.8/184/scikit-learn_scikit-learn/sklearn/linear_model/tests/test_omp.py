# Author: Vlad Niculae
# License: BSD 3 clause

import numpy as np

from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_equal
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

n_samples, n_features, n_nonzero_coefs, n_targets = 20, 30, 5, 3
y, X, gamma = make_sparse_coded_signal(n_targets, n_features, n_samples,
                                       n_nonzero_coefs, random_state=0)
# Make X not of norm 1 for testing
X *= 10
y *= 10
G, Xy = np.dot(X.T, X), np.dot(X.T, y)
# this makes X (n_samples, n_features)
# and y (n_samples, 3)


def test_correct_shapes():
    assert_equal(orthogonal_mp(X, y[:, 0], n_nonzero_coefs=5).shape,
                 (n_features,))
    assert_equal(orthogonal_mp(X, y, n_nonzero_coefs=5).shape,
                 (n_features, 3))


def test_correct_shapes_gram():
    """
    Tests the shape of the output from the orthogonal_mp_gram function.
    
    Parameters
    ----------
    G : array-like, shape (n_features, n_features)
    Gram matrix of the design matrix.
    Xy : array-like, shape (n_features,) or (n_features, n_targets)
    Gram matrix of the target variables.
    n_nonzero_coefs : int, optional
    Desired number of non-zero entries in the solution. If None, it is set
    to n_features // 1
    """

    assert_equal(orthogonal_mp_gram(G, Xy[:, 0], n_nonzero_coefs=5).shape,
                 (n_features,))
    assert_equal(orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5).shape,
                 (n_features, 3))


def test_n_nonzero_coefs():
    assert_true(np.count_nonzero(orthogonal_mp(X, y[:, 0],
                                 n_nonzero_coefs=5)) <= 5)
    assert_true(np.count_nonzero(orthogonal_mp(X, y[:, 0], n_nonzero_coefs=5,
                                               precompute=True)) <= 5)


def test_tol():
    tol = 0.5
    gamma = orthogonal_mp(X, y[:, 0], tol=tol)
    gamma_gram = orthogonal_mp(X, y[:, 0], tol=tol, precompute=True)
    assert_true(np.sum((y[:, 0] - np.dot(X, gamma)) ** 2) <= tol)
    assert_true(np.sum((y[:, 0] - np.dot(X, gamma_gram)) ** 2) <= tol)


def test_with_without_gram():
    assert_array_almost_equal(
        orthogonal_mp(X, y, n_nonzero_coefs=5),
        orthogonal_mp(X, y, n_nonzero_coefs=5, precompute=True))


def test_with_without_gram_tol():
    assert_array_almost_equal(
        orthogonal_mp(X, y, tol=1.),
        orthogonal_mp(X, y, tol=1., precompute=True))


def test_unreachable_accuracy():
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
    """
    Tests the perfect recovery of a signal using orthogonal matching pursuit (OMP) and its Gram matrix variant.
    
    This function checks the perfect recovery of a signal by comparing the original signal indices, the signal recovered using OMP, and the signal recovered using the Gram matrix variant of OMP.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `idx`: Indices of the non-zero elements in the first column of `gamma`.
    - `gamma_rec`: Signal recovered using OMP.
    """

    idx, = gamma[:, 0].nonzero()
    gamma_rec = orthogonal_mp(X, y[:, 0], 5)
    gamma_gram = orthogonal_mp_gram(G, Xy[:, 0], 5)
    assert_array_equal(idx, np.flatnonzero(gamma_rec))
    assert_array_equal(idx, np.flatnonzero(gamma_gram))
    assert_array_almost_equal(gamma[:, 0], gamma_rec, decimal=2)
    assert_array_almost_equal(gamma[:, 0], gamma_gram, decimal=2)


def test_estimator():
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=n_nonzero_coefs)
    omp.fit(X, y[:, 0])
    assert_equal(omp.coef_.shape, (n_features,))
    assert_equal(omp.intercept_.shape, ())
    assert_true(np.count_nonzero(omp.coef_) <= n_nonzero_coefs)

    omp.fit(X, y)
    assert_equal(omp.coef_.shape, (n_targets, n_features))
    assert_equal(omp.intercept_.shape, (n_targets,))
    assert_true(np.count_nonzero(omp.coef_) <= n_targets * n_nonzero_coefs)

    coef_normalized = omp.coef_[0].copy()
    omp.set_params(fit_intercept=True, normalize=False)
    omp.fit(X, y[:, 0])
    assert_array_almost_equal(coef_normalized, omp.coef_)

    omp.set_params(fit_intercept=False, normalize=False)
    omp.fit(X, y[:, 0])
    assert_true(np.count_nonzero(omp.coef_) <= n_nonzero_coefs)
    assert_equal(omp.coef_.shape, (n_features,))
    assert_equal(omp.intercept_, 0)

    omp.fit(X, y)
    assert_equal(omp.coef_.shape, (n_targets, n_features))
    assert_equal(omp.intercept_, 0)
    assert_true(np.count_nonzero(omp.coef_) <= n_targets * n_nonzero_coefs)


def test_identical_regressors():
    newX = X.copy()
    newX[:, 1] = newX[:, 0]
    gamma = np.zeros(n_features)
    gamma[0] = gamma[1] = 1.
    newy = np.dot(newX, gamma)
    assert_warns(RuntimeWarning, orthogonal_mp, newX, newy, 2)


def test_swapped_regressors():
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
    assert_equal(np.all(gamma_empty == 0), True)
    assert_equal(np.all(gamma_empty_gram == 0), True)


def test_omp_path():
    path = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=True)
    last = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=False)
    assert_equal(path.shape, (n_features, n_targets, 5))
    assert_array_almost_equal(path[:, :, -1], last)
    path = orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5, return_path=True)
    last = orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5, return_path=False)
    assert_equal(path.shape, (n_features, n_targets, 5))
    assert_array_almost_equal(path[:, :, -1], last)


def test_omp_return_path_prop_with_gram():
    path = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=True,
                         precompute=True)
    last = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=False,
                         precompute=True)
    assert_equal(path.shape, (n_features, n_targets, 5))
    assert_array_almost_equal(path[:, :, -1], last)


def test_omp_cv():
    """
    Test Orthogonal Matching Pursuit Cross Validation (OMPCV).
    
    This function evaluates the performance of the Orthogonal Matching Pursuit
    Cross Validation (OMPCV) by fitting the model to the input data and comparing
    the results with a manually specified number of non-zero coefficients and
    expected coefficients.
    
    Parameters:
    X (array-like): The input features for the model.
    y (array-like): The target values for the model.
    gamma (array-like): The expected coefficients for comparison.
    """

    y_ = y[:, 0]
    gamma_ = gamma[:, 0]
    ompcv = OrthogonalMatchingPursuitCV(normalize=True, fit_intercept=False,
                                        max_iter=10, cv=5)
    ompcv.fit(X, y_)
    assert_equal(ompcv.n_nonzero_coefs_, n_nonzero_coefs)
    assert_array_almost_equal(ompcv.coef_, gamma_)
    omp = OrthogonalMatchingPursuit(normalize=True, fit_intercept=False,
                                    n_nonzero_coefs=ompcv.n_nonzero_coefs_)
    omp.fit(X, y_)
    assert_array_almost_equal(ompcv.coef_, omp.coef_)


def test_omp_reaches_least_squares():
    """
    Test that OMP reaches least squares solution for a small, simple dataset.
    
    This function checks the Orthogonal Matching Pursuit (OMP) algorithm by comparing
    its solution to the least squares solution for a small, randomly generated dataset.
    The dataset is designed to be simple and small, ensuring that OMP does not stop
    early and instead reaches the least squares solution.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses a small, randomly generated dataset with 1
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
