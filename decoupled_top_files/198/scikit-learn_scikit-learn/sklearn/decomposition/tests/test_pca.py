import numpy as np
import scipy as sp
from itertools import product

import pytest

from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_allclose
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import assert_raise_message
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_raises_regex
from sklearn.utils.testing import assert_no_warnings
from sklearn.utils.testing import ignore_warnings
from sklearn.utils.testing import assert_less

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.decomposition.pca import _assess_dimension_
from sklearn.decomposition.pca import _infer_dimension_

iris = datasets.load_iris()
solver_list = ['full', 'arpack', 'randomized', 'auto']


def test_pca():
    """
    Perform Principal Component Analysis (PCA) on the Iris dataset.
    
    This function tests the functionality of PCA on dense arrays using the Iris dataset. It iterates over a range of principal component numbers and performs PCA using different methods. The function checks the shape of transformed data, compares results from different methods, and validates the covariance and precision matrices.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `PCA`: Performs PCA on the input data.
    - `fit
    """

    # PCA on dense arrays
    X = iris.data

    for n_comp in np.arange(X.shape[1]):
        pca = PCA(n_components=n_comp, svd_solver='full')

        X_r = pca.fit(X).transform(X)
        np.testing.assert_equal(X_r.shape[1], n_comp)

        X_r2 = pca.fit_transform(X)
        assert_array_almost_equal(X_r, X_r2)

        X_r = pca.transform(X)
        X_r2 = pca.fit_transform(X)
        assert_array_almost_equal(X_r, X_r2)

        # Test get_covariance and get_precision
        cov = pca.get_covariance()
        precision = pca.get_precision()
        assert_array_almost_equal(np.dot(cov, precision),
                                  np.eye(X.shape[1]), 12)

    # test explained_variance_ratio_ == 1 with all components
    pca = PCA(svd_solver='full')
    pca.fit(X)
    assert_almost_equal(pca.explained_variance_ratio_.sum(), 1.0, 3)


def test_pca_arpack_solver():
    """
    Test the PCA class with the 'arpack' solver.
    
    This function tests the PCA class using the 'arpack' solver on dense arrays.
    It iterates through various numbers of principal components (excluding the extremes) and performs the following operations:
    - Fits the PCA model to the input data.
    - Transforms the input data using the fitted PCA model.
    - Asserts that the transformed data has the correct number of components.
    - Compares the results of fit_transform and
    """

    # PCA on dense arrays
    X = iris.data
    d = X.shape[1]

    # Loop excluding the extremes, invalid inputs for arpack
    for n_comp in np.arange(1, d):
        pca = PCA(n_components=n_comp, svd_solver='arpack', random_state=0)

        X_r = pca.fit(X).transform(X)
        np.testing.assert_equal(X_r.shape[1], n_comp)

        X_r2 = pca.fit_transform(X)
        assert_array_almost_equal(X_r, X_r2)

        X_r = pca.transform(X)
        assert_array_almost_equal(X_r, X_r2)

        # Test get_covariance and get_precision
        cov = pca.get_covariance()
        precision = pca.get_precision()
        assert_array_almost_equal(np.dot(cov, precision),
                                  np.eye(d), 12)

    pca = PCA(n_components=0, svd_solver='arpack', random_state=0)
    assert_raises(ValueError, pca.fit, X)
    # Check internal state
    assert_equal(pca.n_components,
                 PCA(n_components=0,
                     svd_solver='arpack', random_state=0).n_components)
    assert_equal(pca.svd_solver,
                 PCA(n_components=0,
                     svd_solver='arpack', random_state=0).svd_solver)

    pca = PCA(n_components=d, svd_solver='arpack', random_state=0)
    assert_raises(ValueError, pca.fit, X)
    assert_equal(pca.n_components,
                 PCA(n_components=d,
                     svd_solver='arpack', random_state=0).n_components)
    assert_equal(pca.svd_solver,
                 PCA(n_components=0,
                     svd_solver='arpack', random_state=0).svd_solver)


def test_pca_randomized_solver():
    """
    Performs Principal Component Analysis (PCA) using the randomized solver on dense arrays.
    
    This function tests the functionality of PCA with the 'randomized' solver on dense input arrays. It iterates over a range of principal component numbers, fitting and transforming the data to ensure that the number of components matches the specified value. The function also validates the internal state of the PCA object and raises exceptions for invalid input parameters.
    
    Parameters:
    None (the function uses a predefined dataset 'iris.data')
    """

    # PCA on dense arrays
    X = iris.data

    # Loop excluding the 0, invalid for randomized
    for n_comp in np.arange(1, X.shape[1]):
        pca = PCA(n_components=n_comp, svd_solver='randomized', random_state=0)

        X_r = pca.fit(X).transform(X)
        np.testing.assert_equal(X_r.shape[1], n_comp)

        X_r2 = pca.fit_transform(X)
        assert_array_almost_equal(X_r, X_r2)

        X_r = pca.transform(X)
        assert_array_almost_equal(X_r, X_r2)

        # Test get_covariance and get_precision
        cov = pca.get_covariance()
        precision = pca.get_precision()
        assert_array_almost_equal(np.dot(cov, precision),
                                  np.eye(X.shape[1]), 12)

    pca = PCA(n_components=0, svd_solver='randomized', random_state=0)
    assert_raises(ValueError, pca.fit, X)

    pca = PCA(n_components=0, svd_solver='randomized', random_state=0)
    assert_raises(ValueError, pca.fit, X)
    # Check internal state
    assert_equal(pca.n_components,
                 PCA(n_components=0,
                     svd_solver='randomized', random_state=0).n_components)
    assert_equal(pca.svd_solver,
                 PCA(n_components=0,
                     svd_solver='randomized', random_state=0).svd_solver)


def test_no_empty_slice_warning():
    """
    Test for avoiding numpy warnings when computing PCA on an empty slice.
    
    This function checks that no warnings are raised when performing Principal
    Component Analysis (PCA) on an array with dimensions greater than the
    specified number of components. The function creates a random array `X` with
    shape (n_components, n_features), where `n_features` is set to be greater
    than `n_components`. It then initializes a PCA object with `n_components`
    and asserts that no
    """

    # test if we avoid numpy warnings for computing over empty arrays
    n_components = 10
    n_features = n_components + 2  # anything > n_comps triggered it in 0.16
    X = np.random.uniform(-1, 1, size=(n_components, n_features))
    pca = PCA(n_components=n_components)
    assert_no_warnings(pca.fit, X)


def test_whitening():
    """
    Whitens and reduces dimensionality of input data using Principal Component Analysis (PCA).
    
    This function performs PCA on the input data `X` and whitens the transformed data such that each principal component has unit variance. It also projects the data onto a lower-dimensional subspace defined by `n_components`.
    
    Parameters:
    None (the parameters are derived from the function's internal setup)
    
    Returns:
    - X_whitened: The whitened and reduced-dimensional data.
    - X_un
    """

    # Check that PCA output has unit-variance
    rng = np.random.RandomState(0)
    n_samples = 100
    n_features = 80
    n_components = 30
    rank = 50

    # some low rank data with correlated features
    X = np.dot(rng.randn(n_samples, rank),
               np.dot(np.diag(np.linspace(10.0, 1.0, rank)),
                      rng.randn(rank, n_features)))
    # the component-wise variance of the first 50 features is 3 times the
    # mean component-wise variance of the remaining 30 features
    X[:, :50] *= 3

    assert_equal(X.shape, (n_samples, n_features))

    # the component-wise variance is thus highly varying:
    assert_greater(X.std(axis=0).std(), 43.8)

    for solver, copy in product(solver_list, (True, False)):
        # whiten the data while projecting to the lower dim subspace
        X_ = X.copy()  # make sure we keep an original across iterations.
        pca = PCA(n_components=n_components, whiten=True, copy=copy,
                  svd_solver=solver, random_state=0, iterated_power=7)
        # test fit_transform
        X_whitened = pca.fit_transform(X_.copy())
        assert_equal(X_whitened.shape, (n_samples, n_components))
        X_whitened2 = pca.transform(X_)
        assert_array_almost_equal(X_whitened, X_whitened2)

        assert_almost_equal(X_whitened.std(ddof=1, axis=0),
                            np.ones(n_components),
                            decimal=6)
        assert_almost_equal(X_whitened.mean(axis=0), np.zeros(n_components))

        X_ = X.copy()
        pca = PCA(n_components=n_components, whiten=False, copy=copy,
                  svd_solver=solver).fit(X_)
        X_unwhitened = pca.transform(X_)
        assert_equal(X_unwhitened.shape, (n_samples, n_components))

        # in that case the output components still have varying variances
        assert_almost_equal(X_unwhitened.std(axis=0).std(), 74.1, 1)
        # we always center, so no test for non-centering.


# Ignore warnings from switching to more power iterations in randomized_svd
@ignore_warnings
def test_explained_variance():
    """
    Test the explained variance of PCA.
    
    This function checks the correctness of the explained variance and its ratio
    for different solvers (full, arpack, randomized) on both uncorrelated and
    correlated data. It ensures that the output of PCA has unit variance and
    compares the results with the empirical variances calculated using numpy's
    `linalg.eig` and `cov` functions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    """

    # Check that PCA output has unit-variance
    rng = np.random.RandomState(0)
    n_samples = 100
    n_features = 80

    X = rng.randn(n_samples, n_features)

    pca = PCA(n_components=2, svd_solver='full').fit(X)
    apca = PCA(n_components=2, svd_solver='arpack', random_state=0).fit(X)
    assert_array_almost_equal(pca.explained_variance_,
                              apca.explained_variance_, 1)
    assert_array_almost_equal(pca.explained_variance_ratio_,
                              apca.explained_variance_ratio_, 3)

    rpca = PCA(n_components=2, svd_solver='randomized', random_state=42).fit(X)
    assert_array_almost_equal(pca.explained_variance_,
                              rpca.explained_variance_, 1)
    assert_array_almost_equal(pca.explained_variance_ratio_,
                              rpca.explained_variance_ratio_, 1)

    # compare to empirical variances
    expected_result = np.linalg.eig(np.cov(X, rowvar=False))[0]
    expected_result = sorted(expected_result, reverse=True)[:2]

    X_pca = pca.transform(X)
    assert_array_almost_equal(pca.explained_variance_,
                              np.var(X_pca, ddof=1, axis=0))
    assert_array_almost_equal(pca.explained_variance_, expected_result)

    X_pca = apca.transform(X)
    assert_array_almost_equal(apca.explained_variance_,
                              np.var(X_pca, ddof=1, axis=0))
    assert_array_almost_equal(apca.explained_variance_, expected_result)

    X_rpca = rpca.transform(X)
    assert_array_almost_equal(rpca.explained_variance_,
                              np.var(X_rpca, ddof=1, axis=0),
                              decimal=1)
    assert_array_almost_equal(rpca.explained_variance_,
                              expected_result, decimal=1)

    # Same with correlated data
    X = datasets.make_classification(n_samples, n_features,
                                     n_informative=n_features-2,
                                     random_state=rng)[0]

    pca = PCA(n_components=2).fit(X)
    rpca = PCA(n_components=2, svd_solver='randomized',
               random_state=rng).fit(X)
    assert_array_almost_equal(pca.explained_variance_ratio_,
                              rpca.explained_variance_ratio_, 5)


def test_singular_values():
    """
    Test the singular values returned by different PCA solvers.
    
    This function checks the correctness of the singular values produced by
    three different PCA solvers: 'full', 'arpack', and 'randomized'. It also
    verifies the consistency of these singular values with the Frobenius norm
    and the 2-norms of the score vectors. Additionally, it tests the behavior
    when setting the singular values and observing the resulting transformation.
    
    Parameters:
    None (the
    """

    # Check that the PCA output has the correct singular values

    rng = np.random.RandomState(0)
    n_samples = 100
    n_features = 80

    X = rng.randn(n_samples, n_features)

    pca = PCA(n_components=2, svd_solver='full',
              random_state=rng).fit(X)
    apca = PCA(n_components=2, svd_solver='arpack',
               random_state=rng).fit(X)
    rpca = PCA(n_components=2, svd_solver='randomized',
               random_state=rng).fit(X)
    assert_array_almost_equal(pca.singular_values_, apca.singular_values_, 12)
    assert_array_almost_equal(pca.singular_values_, rpca.singular_values_, 1)
    assert_array_almost_equal(apca.singular_values_, rpca.singular_values_, 1)

    # Compare to the Frobenius norm
    X_pca = pca.transform(X)
    X_apca = apca.transform(X)
    X_rpca = rpca.transform(X)
    assert_array_almost_equal(np.sum(pca.singular_values_**2.0),
                              np.linalg.norm(X_pca, "fro")**2.0, 12)
    assert_array_almost_equal(np.sum(apca.singular_values_**2.0),
                              np.linalg.norm(X_apca, "fro")**2.0, 9)
    assert_array_almost_equal(np.sum(rpca.singular_values_**2.0),
                              np.linalg.norm(X_rpca, "fro")**2.0, 0)

    # Compare to the 2-norms of the score vectors
    assert_array_almost_equal(pca.singular_values_,
                              np.sqrt(np.sum(X_pca**2.0, axis=0)), 12)
    assert_array_almost_equal(apca.singular_values_,
                              np.sqrt(np.sum(X_apca**2.0, axis=0)), 12)
    assert_array_almost_equal(rpca.singular_values_,
                              np.sqrt(np.sum(X_rpca**2.0, axis=0)), 2)

    # Set the singular values and see what we get back
    rng = np.random.RandomState(0)
    n_samples = 100
    n_features = 110

    X = rng.randn(n_samples, n_features)

    pca = PCA(n_components=3, svd_solver='full', random_state=rng)
    apca = PCA(n_components=3, svd_solver='arpack', random_state=rng)
    rpca = PCA(n_components=3, svd_solver='randomized', random_state=rng)
    X_pca = pca.fit_transform(X)

    X_pca /= np.sqrt(np.sum(X_pca**2.0, axis=0))
    X_pca[:, 0] *= 3.142
    X_pca[:, 1] *= 2.718

    X_hat = np.dot(X_pca, pca.components_)
    pca.fit(X_hat)
    apca.fit(X_hat)
    rpca.fit(X_hat)
    assert_array_almost_equal(pca.singular_values_, [3.142, 2.718, 1.0], 14)
    assert_array_almost_equal(apca.singular_values_, [3.142, 2.718, 1.0], 14)
    assert_array_almost_equal(rpca.singular_values_, [3.142, 2.718, 1.0], 14)


def test_pca_check_projection():
    """
    Test the correctness of the projection of data using Principal Component Analysis (PCA).
    
    This function checks if the projection of given test data `Xt` onto the principal components derived from training data `X` is accurate. It iterates over different solvers for PCA computation and ensures that the first component of the transformed test data has a unit norm and a significant magnitude.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: The main function used for
    """

    # Test that the projection of data is correct
    rng = np.random.RandomState(0)
    n, p = 100, 3
    X = rng.randn(n, p) * .1
    X[:10] += np.array([3, 4, 5])
    Xt = 0.1 * rng.randn(1, p) + np.array([3, 4, 5])

    for solver in solver_list:
        Yt = PCA(n_components=2, svd_solver=solver).fit(X).transform(Xt)
        Yt /= np.sqrt((Yt ** 2).sum())

        assert_almost_equal(np.abs(Yt[0][0]), 1., 1)


def test_pca_inverse():
    """
    Test the inverse transformation of PCA.
    
    This function tests whether the projection of data using PCA can be accurately inverted. It does this by first generating a dataset with specific characteristics: high variance in some dimensions, low variance in others, and a large mean. The PCA is then applied to this data, and the transformed data is reconstructed using the inverse transform method. The function checks if the reconstructed data matches the original data within a certain precision level.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Test that the projection of data can be inverted
    rng = np.random.RandomState(0)
    n, p = 50, 3
    X = rng.randn(n, p)  # spherical data
    X[:, 1] *= .00001  # make middle component relatively small
    X += [5, 4, 3]  # make a large mean

    # same check that we can find the original data from the transformed
    # signal (since the data is almost of rank n_components)
    pca = PCA(n_components=2, svd_solver='full').fit(X)
    Y = pca.transform(X)
    Y_inverse = pca.inverse_transform(Y)
    assert_almost_equal(X, Y_inverse, decimal=3)

    # same as above with whitening (approximate reconstruction)
    for solver in solver_list:
        pca = PCA(n_components=2, whiten=True, svd_solver=solver)
        pca.fit(X)
        Y = pca.transform(X)
        Y_inverse = pca.inverse_transform(Y)
        assert_almost_equal(X, Y_inverse, decimal=3)


@pytest.mark.parametrize('solver', solver_list)
def test_pca_validation(solver):
    """
    Ensures that the specified solver handles extreme values for the n_components parameter correctly.
    
    This function validates that the given solver raises appropriate errors when invalid values are passed to the n_components parameter. It tests this by fitting a PCA model with different configurations and checking for expected exceptions.
    
    Parameters:
    solver (str): The solver to use for the PCA decomposition ('randomized', 'arpack', 'full', or 'auto').
    
    Returns:
    None: The function does not return any value
    """

    # Ensures that solver-specific extreme inputs for the n_components
    # parameter raise errors
    X = np.array([[0, 1, 0], [1, 0, 0]])
    smallest_d = 2  # The smallest dimension
    lower_limit = {'randomized': 1, 'arpack': 1, 'full': 0, 'auto': 0}

    # We conduct the same test on X.T so that it is invariant to axis.
    for data in [X, X.T]:
        for n_components in [-1, 3]:

            if solver == 'auto':
                solver_reported = 'full'
            else:
                solver_reported = solver

            assert_raises_regex(ValueError,
                                "n_components={}L? must be between "
                                r"{}L? and min\(n_samples, n_features\)="
                                "{}L? with svd_solver=\'{}\'"
                                .format(n_components,
                                        lower_limit[solver],
                                        smallest_d,
                                        solver_reported),
                                PCA(n_components,
                                    svd_solver=solver).fit, data)
        if solver == 'arpack':

            n_components = smallest_d

            assert_raises_regex(ValueError,
                                "n_components={}L? must be "
                                "strictly less than "
                                r"min\(n_samples, n_features\)={}L?"
                                " with svd_solver=\'arpack\'"
                                .format(n_components, smallest_d),
                                PCA(n_components, svd_solver=solver)
                                .fit, data)

    n_components = 1.0
    type_ncom = type(n_components)
    assert_raise_message(ValueError,
                         "n_components={} must be of type int "
                         "when greater than or equal to 1, was of type={}"
                         .format(n_components, type_ncom),
                         PCA(n_components, svd_solver=solver).fit, data)


@pytest.mark.parametrize('solver', solver_list)
def test_n_components_none(solver):
    """
    Test handling of `n_components=None` in PCA.
    
    This function ensures that when `n_components=None`, the PCA object
    correctly determines the number of components based on the input data.
    The function iterates over both the original and transposed versions of
    the Iris dataset to ensure the behavior is consistent regardless of the
    axis along which the transformation is applied.
    
    Parameters:
    solver (str): The solver to use for PCA decomposition ('auto', 'full', 'random
    """

    # Ensures that n_components == None is handled correctly
    X = iris.data
    # We conduct the same test on X.T so that it is invariant to axis.
    for data in [X, X.T]:
        pca = PCA(svd_solver=solver)
        pca.fit(data)
        if solver == 'arpack':
            assert_equal(pca.n_components_, min(data.shape) - 1)
        else:
            assert_equal(pca.n_components_, min(data.shape))


def test_randomized_pca_check_projection():
    """
    Test the correctness of projection using randomized PCA on dense data.
    
    This function checks if the projection of a test vector `Xt` onto the
    principal components obtained from fitting the training data `X` using
    randomized PCA results in a unit vector along the first principal component.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: Performs Principal Component Analysis using the 'randomized' solver.
    - `fit`: Fits the PCA model
    """

    # Test that the projection by randomized PCA on dense data is correct
    rng = np.random.RandomState(0)
    n, p = 100, 3
    X = rng.randn(n, p) * .1
    X[:10] += np.array([3, 4, 5])
    Xt = 0.1 * rng.randn(1, p) + np.array([3, 4, 5])

    Yt = PCA(n_components=2, svd_solver='randomized',
             random_state=0).fit(X).transform(Xt)
    Yt /= np.sqrt((Yt ** 2).sum())

    assert_almost_equal(np.abs(Yt[0][0]), 1., 1)


def test_randomized_pca_check_list():
    """
    Test the projection of list data using randomized PCA.
    
    This function verifies that the transformed data after applying
    randomized PCA has the expected shape, mean, and standard deviation.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: Applies Principal Component Analysis with the 'randomized' solver.
    - `fit`: Fits the PCA model to the input data.
    - `transform`: Transforms the input data using the fitted PCA model.
    
    Input
    """

    # Test that the projection by randomized PCA on list data is correct
    X = [[1.0, 0.0], [0.0, 1.0]]
    X_transformed = PCA(n_components=1, svd_solver='randomized',
                        random_state=0).fit(X).transform(X)
    assert_equal(X_transformed.shape, (2, 1))
    assert_almost_equal(X_transformed.mean(), 0.00, 2)
    assert_almost_equal(X_transformed.std(), 0.71, 2)


def test_randomized_pca_inverse():
    """
    Test the inverse transformation of Randomized PCA on dense data.
    
    This function checks if the original data can be accurately reconstructed
    from its transformed representation using Randomized PCA. It performs two
    tests: one without whitening and another with whitening. The function uses
    the following key components:
    
    - `PCA`: A class from scikit-learn's decomposition module for performing
    principal component analysis.
    - `fit`: Method to fit the PCA model to the input data
    """

    # Test that randomized PCA is inversible on dense data
    rng = np.random.RandomState(0)
    n, p = 50, 3
    X = rng.randn(n, p)  # spherical data
    X[:, 1] *= .00001  # make middle component relatively small
    X += [5, 4, 3]  # make a large mean

    # same check that we can find the original data from the transformed signal
    # (since the data is almost of rank n_components)
    pca = PCA(n_components=2, svd_solver='randomized', random_state=0).fit(X)
    Y = pca.transform(X)
    Y_inverse = pca.inverse_transform(Y)
    assert_almost_equal(X, Y_inverse, decimal=2)

    # same as above with whitening (approximate reconstruction)
    pca = PCA(n_components=2, whiten=True, svd_solver='randomized',
              random_state=0).fit(X)
    Y = pca.transform(X)
    Y_inverse = pca.inverse_transform(Y)
    relative_max_delta = (np.abs(X - Y_inverse) / np.abs(X).mean()).max()
    assert_less(relative_max_delta, 1e-5)


def test_n_components_mle():
    """
    Test the behavior of PCA when using 'mle' as the n_components value.
    
    This function ensures that:
    - Using 'mle' as n_components does not raise an error for 'auto' or 'full'
    svd solvers.
    - Using 'mle' as n_components raises an error for 'arpack' or 'randomized'
    svd solvers.
    
    Parameters:
    - X (numpy.ndarray): The input data matrix of shape (n_samples
    """

    # Ensure that n_components == 'mle' doesn't raise error for auto/full
    # svd_solver and raises error for arpack/randomized svd_solver
    rng = np.random.RandomState(0)
    n_samples = 600
    n_features = 10
    X = rng.randn(n_samples, n_features)
    n_components_dict = {}
    for solver in solver_list:
        pca = PCA(n_components='mle', svd_solver=solver)
        if solver in ['auto', 'full']:
            pca.fit(X)
            n_components_dict[solver] = pca.n_components_
        else:  # arpack/randomized solver
            error_message = ("n_components='mle' cannot be a string with "
                             "svd_solver='{}'".format(solver))
            assert_raise_message(ValueError, error_message, pca.fit, X)
    assert_equal(n_components_dict['auto'], n_components_dict['full'])


def test_pca_dim():
    """
    Automatically determine the optimal number of principal components using Maximum Likelihood Estimation (MLE).
    
    This function fits a Principal Component Analysis (PCA) model to the input data `X` and determines the optimal number of components based on Maximum Likelihood Estimation. The function uses the 'full' solver method for singular value decomposition.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Notes:
    ------
    - The input data `X` is modified by
    """

    # Check automated dimensionality setting
    rng = np.random.RandomState(0)
    n, p = 100, 5
    X = rng.randn(n, p) * .1
    X[:10] += np.array([3, 4, 5, 1, 2])
    pca = PCA(n_components='mle', svd_solver='full').fit(X)
    assert_equal(pca.n_components, 'mle')
    assert_equal(pca.n_components_, 1)


def test_infer_dim_1():
    """
    Tests the inference of the optimal dimension using the _assess_dimension_ function.
    
    This function evaluates the explained variance of a dataset after applying PCA with different numbers of components. It then assesses the optimal dimension by comparing the log-likelihood values obtained from the _assess_dimension_ function for each possible number of components. The test asserts that the log-likelihood for two components is higher than the maximum log-likelihood minus 0.01 times the number of samples.
    
    Parameters:
    """

    # TODO: explain what this is testing
    # Or at least use explicit variable names...
    n, p = 1000, 5
    rng = np.random.RandomState(0)
    X = (rng.randn(n, p) * .1 + rng.randn(n, 1) * np.array([3, 4, 5, 1, 2]) +
         np.array([1, 0, 7, 4, 6]))
    pca = PCA(n_components=p, svd_solver='full')
    pca.fit(X)
    spect = pca.explained_variance_
    ll = np.array([_assess_dimension_(spect, k, n, p) for k in range(p)])
    assert_greater(ll[1], ll.max() - .01 * n)


def test_infer_dim_2():
    """
    Infer the number of principal components that explain a significant amount of variance in the data.
    
    This function uses the explained variance ratio from a Principal Component Analysis (PCA) to determine the minimum number of components needed to capture a specified proportion of the total variance. The function takes into account the dimensions of the input data and applies a threshold to identify the effective number of components.
    
    Parameters:
    - spect (array-like): The explained variance ratios obtained from PCA.
    - n (int): The
    """

    # TODO: explain what this is testing
    # Or at least use explicit variable names...
    n, p = 1000, 5
    rng = np.random.RandomState(0)
    X = rng.randn(n, p) * .1
    X[:10] += np.array([3, 4, 5, 1, 2])
    X[10:20] += np.array([6, 0, 7, 2, -1])
    pca = PCA(n_components=p, svd_solver='full')
    pca.fit(X)
    spect = pca.explained_variance_
    assert_greater(_infer_dimension_(spect, n, p), 1)


def test_infer_dim_3():
    """
    Infer the number of significant principal components from the explained variance spectrum.
    
    This function takes the explained variance spectrum obtained from fitting a PCA model to data,
    along with the number of samples (n) and features (p), and determines the minimum number of
    principal components that explain a significant amount of variance.
    
    Parameters:
    -----------
    spect : array-like
    The explained variance spectrum obtained from fitting a PCA model.
    n : int
    Number of samples in the dataset
    """

    n, p = 100, 5
    rng = np.random.RandomState(0)
    X = rng.randn(n, p) * .1
    X[:10] += np.array([3, 4, 5, 1, 2])
    X[10:20] += np.array([6, 0, 7, 2, -1])
    X[30:40] += 2 * np.array([-1, 1, -1, 1, -1])
    pca = PCA(n_components=p, svd_solver='full')
    pca.fit(X)
    spect = pca.explained_variance_
    assert_greater(_infer_dimension_(spect, n, p), 2)


def test_infer_dim_by_explained_variance():
    """
    Infer the number of principal components by explained variance.
    
    This function tests the inference of the optimal number of principal
    components based on the specified explained variance ratio using the PCA
    (Principal Component Analysis) method with full singular value decomposition
    solver.
    
    Parameters:
    None
    
    Returns:
    None
    
    Tests:
    - For `n_components=0.95`, the inferred number of components is 2.
    - For `n_components=0.01
    """

    X = iris.data
    pca = PCA(n_components=0.95, svd_solver='full')
    pca.fit(X)
    assert_equal(pca.n_components, 0.95)
    assert_equal(pca.n_components_, 2)

    pca = PCA(n_components=0.01, svd_solver='full')
    pca.fit(X)
    assert_equal(pca.n_components, 0.01)
    assert_equal(pca.n_components_, 1)

    rng = np.random.RandomState(0)
    # more features than samples
    X = rng.rand(5, 20)
    pca = PCA(n_components=.5, svd_solver='full').fit(X)
    assert_equal(pca.n_components, 0.5)
    assert_equal(pca.n_components_, 2)


def test_pca_score():
    """
    Test the scoring method of Probabilistic Principal Component Analysis (PCA).
    
    This function evaluates the performance of the `score` method in the PCA
    class by comparing the log-likelihood of the data under the fitted model
    with an expected value. The test is performed using different solvers
    specified in `solver_list`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: Fits the probabilistic PCA model to the input data.
    """

    # Test that probabilistic PCA scoring yields a reasonable score
    n, p = 1000, 3
    rng = np.random.RandomState(0)
    X = rng.randn(n, p) * .1 + np.array([3, 4, 5])
    for solver in solver_list:
        pca = PCA(n_components=2, svd_solver=solver)
        pca.fit(X)
        ll1 = pca.score(X)
        h = -0.5 * np.log(2 * np.pi * np.exp(1) * 0.1 ** 2) * p
        np.testing.assert_almost_equal(ll1 / h, 1, 0)


def test_pca_score2():
    """
    Test the performance of probabilistic PCA on different datasets.
    
    This function evaluates the score of probabilistic PCA on two sets of data:
    - The first set `X` is generated with a small noise and a specific mean.
    - The second set is generated with a larger noise and the same mean as the first set.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: Used to fit the probabilistic PCA model to the data.
    """

    # Test that probabilistic PCA correctly separated different datasets
    n, p = 100, 3
    rng = np.random.RandomState(0)
    X = rng.randn(n, p) * .1 + np.array([3, 4, 5])
    for solver in solver_list:
        pca = PCA(n_components=2, svd_solver=solver)
        pca.fit(X)
        ll1 = pca.score(X)
        ll2 = pca.score(rng.randn(n, p) * .2 + np.array([3, 4, 5]))
        assert_greater(ll1, ll2)

        # Test that it gives different scores if whiten=True
        pca = PCA(n_components=2, whiten=True, svd_solver=solver)
        pca.fit(X)
        ll2 = pca.score(X)
        assert ll1 > ll2


def test_pca_score3():
    """
    Tests the performance of Probabilistic PCA on selecting the appropriate number of components.
    
    This function evaluates the score of a Probabilistic PCA model on a test dataset `Xt`
    for different numbers of components (`k`). The scores are computed by fitting the model
    to a training dataset `Xl` and then evaluating it on `Xt`. The function asserts that
    the maximum score is achieved when `k` equals 1, indicating that one component is optimal
    """

    # Check that probabilistic PCA selects the right model
    n, p = 200, 3
    rng = np.random.RandomState(0)
    Xl = (rng.randn(n, p) + rng.randn(n, 1) * np.array([3, 4, 5]) +
          np.array([1, 0, 7]))
    Xt = (rng.randn(n, p) + rng.randn(n, 1) * np.array([3, 4, 5]) +
          np.array([1, 0, 7]))
    ll = np.zeros(p)
    for k in range(p):
        pca = PCA(n_components=k, svd_solver='full')
        pca.fit(Xl)
        ll[k] = pca.score(Xt)

    assert ll.argmax() == 1


def test_pca_score_with_different_solvers():
    """
    Tests the PCA score method using different solvers.
    
    This function evaluates the PCA score for the `digits` dataset using various
    solvers ('full', 'arpack', 'randomized'). It ensures that the explained
    variance minus the noise variance is non-negative for each solver. The
    function then compares the scores obtained from these solvers and asserts
    that they are approximately equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    -
    """

    digits = datasets.load_digits()
    X_digits = digits.data

    pca_dict = {svd_solver: PCA(n_components=30, svd_solver=svd_solver,
                                random_state=0)
                for svd_solver in solver_list}

    for pca in pca_dict.values():
        pca.fit(X_digits)
        # Sanity check for the noise_variance_. For more details see
        # https://github.com/scikit-learn/scikit-learn/issues/7568
        # https://github.com/scikit-learn/scikit-learn/issues/8541
        # https://github.com/scikit-learn/scikit-learn/issues/8544
        assert np.all((pca.explained_variance_ - pca.noise_variance_) >= 0)

    # Compare scores with different svd_solvers
    score_dict = {svd_solver: pca.score(X_digits)
                  for svd_solver, pca in pca_dict.items()}
    assert_almost_equal(score_dict['full'], score_dict['arpack'])
    assert_almost_equal(score_dict['full'], score_dict['randomized'],
                        decimal=3)


def test_pca_zero_noise_variance_edge_cases():
    """
    Ensures that the noise variance is zero in edge cases where the number of principal components (n_components) is equal to the minimum of the number of samples (n_samples) or features (n_features). The function tests this behavior using the PCA class from scikit-learn with different singular value decomposition solvers ('full' and 'randomized').
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: The Principal Component Analysis class from scikit
    """

    # ensure that noise_variance_ is 0 in edge cases
    # when n_components == min(n_samples, n_features)
    n, p = 100, 3

    rng = np.random.RandomState(0)
    X = rng.randn(n, p) * .1 + np.array([3, 4, 5])
    # arpack raises ValueError for n_components == min(n_samples,
    # n_features)
    svd_solvers = ['full', 'randomized']

    for svd_solver in svd_solvers:
        pca = PCA(svd_solver=svd_solver, n_components=p)
        pca.fit(X)
        assert pca.noise_variance_ == 0

        pca.fit(X.T)
        assert pca.noise_variance_ == 0


def test_svd_solver_auto():
    """
    Tests the automatic selection of the SVD solver in PCA.
    
    This function evaluates the automatic selection of the SVD solver in PCA
    based on the given input matrix `X`. The solver is chosen based on the
    following criteria:
    
    - If `n_components` is in the range (0, 1), the solver is set to 'full'.
    - If the maximum dimension of `X` is less than or equal to 500, the solver
    is
    """

    rng = np.random.RandomState(0)
    X = rng.uniform(size=(1000, 50))

    # case: n_components in (0,1) => 'full'
    pca = PCA(n_components=.5)
    pca.fit(X)
    pca_test = PCA(n_components=.5, svd_solver='full')
    pca_test.fit(X)
    assert_array_almost_equal(pca.components_, pca_test.components_)

    # case: max(X.shape) <= 500 => 'full'
    pca = PCA(n_components=5, random_state=0)
    Y = X[:10, :]
    pca.fit(Y)
    pca_test = PCA(n_components=5, svd_solver='full', random_state=0)
    pca_test.fit(Y)
    assert_array_almost_equal(pca.components_, pca_test.components_)

    # case: n_components >= .8 * min(X.shape) => 'full'
    pca = PCA(n_components=50)
    pca.fit(X)
    pca_test = PCA(n_components=50, svd_solver='full')
    pca_test.fit(X)
    assert_array_almost_equal(pca.components_, pca_test.components_)

    # n_components >= 1 and n_components < .8 * min(X.shape) => 'randomized'
    pca = PCA(n_components=10, random_state=0)
    pca.fit(X)
    pca_test = PCA(n_components=10, svd_solver='randomized', random_state=0)
    pca_test.fit(X)
    assert_array_almost_equal(pca.components_, pca_test.components_)


@pytest.mark.parametrize('svd_solver', solver_list)
def test_pca_sparse_input(svd_solver):
    """
    Test that PCA raises a TypeError when given a sparse input matrix.
    
    This function checks whether PCA raises a TypeError when provided with
    a sparse input matrix using the specified `svd_solver`. The input matrix
    is generated randomly and converted to a CSR sparse matrix. The function
    asserts that the input is indeed sparse and then attempts to fit a PCA
    model with the specified number of components and solver. If the input is
    sparse, a TypeError should be raised during the
    """

    X = np.random.RandomState(0).rand(5, 4)
    X = sp.sparse.csr_matrix(X)
    assert(sp.sparse.issparse(X))

    pca = PCA(n_components=3, svd_solver=svd_solver)

    assert_raises(TypeError, pca.fit, X)


def test_pca_bad_solver():
    """
    Test that an error is raised when an invalid solver is specified for PCA.
    
    This function checks if a `ValueError` is raised when attempting to fit
    a PCA model with an invalid solver ('bad_argument'). The input data `X`
    is a randomly generated 2D array of shape (5, 4) using NumPy's random
    number generator. The PCA model is initialized with three components and
    the specified invalid solver. The function asserts that fitting the model
    """

    X = np.random.RandomState(0).rand(5, 4)
    pca = PCA(n_components=3, svd_solver='bad_argument')
    assert_raises(ValueError, pca.fit, X)


@pytest.mark.parametrize('svd_solver', solver_list)
def test_pca_dtype_preservation(svd_solver):
    check_pca_float_dtype_preservation(svd_solver)
    check_pca_int_dtype_upcast_to_double(svd_solver)


def test_pca_deterministic_output():
    """
    Tests the deterministic output of PCA using different solvers.
    
    This function ensures that the PCA transformation produces consistent results
    across multiple runs with the same random state. It iterates over a set of
    solvers, fits the PCA model to a randomly generated dataset, and checks if
    the transformed data is identical across all iterations.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `PCA`: The Principal Component Analysis class from scikit-learn
    """

    rng = np.random.RandomState(0)
    X = rng.rand(10, 10)

    for solver in solver_list:
        transformed_X = np.zeros((20, 2))
        for i in range(20):
            pca = PCA(n_components=2, svd_solver=solver, random_state=rng)
            transformed_X[i, :] = pca.fit_transform(X)[0]
        assert_allclose(
            transformed_X, np.tile(transformed_X[0, :], 20).reshape(20, 2))


def check_pca_float_dtype_preservation(svd_solver):
    """
    Ensures that Principal Component Analysis (PCA) preserves the data type of the input when using different solvers.
    
    This function checks that PCA does not upscale the data type when the input is of `float32` type. It compares the results of fitting PCA on both `float64` and `float32` data types, ensuring that the components and transformed data maintain their respective data types.
    
    Parameters:
    svd_solver (str): The solver to use for computing Principal
    """

    # Ensure that PCA does not upscale the dtype when input is float32
    X_64 = np.random.RandomState(0).rand(1000, 4).astype(np.float64,
                                                         copy=False)
    X_32 = X_64.astype(np.float32)

    pca_64 = PCA(n_components=3, svd_solver=svd_solver,
                 random_state=0).fit(X_64)
    pca_32 = PCA(n_components=3, svd_solver=svd_solver,
                 random_state=0).fit(X_32)

    assert pca_64.components_.dtype == np.float64
    assert pca_32.components_.dtype == np.float32
    assert pca_64.transform(X_64).dtype == np.float64
    assert pca_32.transform(X_32).dtype == np.float32

    # decimal=5 fails on mac with scipy = 1.1.0
    assert_array_almost_equal(pca_64.components_, pca_32.components_,
                              decimal=4)


def check_pca_int_dtype_upcast_to_double(svd_solver):
    """
    Ensures that integer data types are upcast to float64 during Principal Component Analysis (PCA) computation.
    
    This function checks that both 64-bit and 32-bit integer inputs result in float64 data types for the PCA components and transformed data, regardless of the integer type used. It uses the `PCA` class from scikit-learn to fit models on randomly generated integer arrays and compares the results.
    
    Parameters:
    svd_solver (str): The solver to use
    """

    # Ensure that all int types will be upcast to float64
    X_i64 = np.random.RandomState(0).randint(0, 1000, (1000, 4))
    X_i64 = X_i64.astype(np.int64, copy=False)
    X_i32 = X_i64.astype(np.int32, copy=False)

    pca_64 = PCA(n_components=3, svd_solver=svd_solver,
                 random_state=0).fit(X_i64)
    pca_32 = PCA(n_components=3, svd_solver=svd_solver,
                 random_state=0).fit(X_i32)

    assert pca_64.components_.dtype == np.float64
    assert pca_32.components_.dtype == np.float64
    assert pca_64.transform(X_i64).dtype == np.float64
    assert pca_32.transform(X_i32).dtype == np.float64

    assert_array_almost_equal(pca_64.components_, pca_32.components_,
                              decimal=5)
