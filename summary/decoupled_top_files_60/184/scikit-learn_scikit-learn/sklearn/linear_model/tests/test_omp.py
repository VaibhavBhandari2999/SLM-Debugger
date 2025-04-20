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
    Test the correctness of the shapes returned by the orthogonal_mp_gram function.
    
    Parameters:
    G (numpy.ndarray): The Gram matrix of the input data.
    Xy (numpy.ndarray): The target values in matrix form.
    n_nonzero_coefs (int): The number of nonzero coefficients to select.
    
    Returns:
    tuple: A tuple containing the shape of the output from the function for a single sample and for multiple samples.
    """

    assert_equal(orthogonal_mp_gram(G, Xy[:, 0], n_nonzero_coefs=5).shape,
                 (n_features,))
    assert_equal(orthogonal_mp_gram(G, Xy, n_nonzero_coefs=5).shape,
                 (n_features, 3))


def test_n_nonzero_coefs():
    """
    Test the number of nonzero coefficients in the orthogonal matching pursuit.
    
    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
    The input data matrix.
    y : array-like, shape (n_samples,)
    The target vector.
    n_nonzero_coefs : int, optional
    The number of nonzero coefficients to select.
    
    Keyword Arguments
    -----------------
    precompute : bool, optional
    Whether to use the precomputed Gram matrix to speed up calculations.
    
    Returns
    -------
    result : bool
    """

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
    """
    Test the equivalence of orthogonal_mp and orthogonal_mp_gram.
    
    Parameters:
    X (array-like): The input data matrix.
    y (array-like): The target vector.
    
    Keyword Arguments:
    n_nonzero_coefs (int): The number of nonzero coefficients for the solution.
    
    Returns:
    bool: True if the results from both functions are almost equal, False otherwise.
    """

    assert_array_almost_equal(
        orthogonal_mp(X, y, n_nonzero_coefs=5),
        orthogonal_mp(X, y, n_nonzero_coefs=5, precompute=True))


def test_with_without_gram_tol():
    """
    Test the orthogonal_mp function with and without gram_tol parameter.
    
    Parameters:
    X (array-like): The input data matrix.
    y (array-like): The target vector.
    
    Returns:
    tuple: A tuple containing the results of orthogonal_mp with and without the gram_tol parameter.
    """

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
    The tolerance for the stopping condition. Default is 0.
    n_features : int
    The number of features in the input data matrix.
    
    Returns
    -------
    result : array-like, shape (n_features,)
    The estimated coefficients from
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
    """
    Return the solution path using Orthogonal Matching Pursuit (OMP) with Gram matrix precomputation.
    
    Parameters:
    X (array-like): Input data matrix.
    y (array-like): Target values.
    n_nonzero_coefs (int): Desired number of non-zero entries in the solution.
    return_path (bool): Whether to return the entire path or just the last column.
    precompute (bool): Whether to use precomputed Gram matrices to speed up calculations.
    
    Returns:
    path
    """

    path = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=True,
                         precompute=True)
    last = orthogonal_mp(X, y, n_nonzero_coefs=5, return_path=False,
                         precompute=True)
    assert_equal(path.shape, (n_features, n_targets, 5))
    assert_array_almost_equal(path[:, :, -1], last)


def test_omp_cv():
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
