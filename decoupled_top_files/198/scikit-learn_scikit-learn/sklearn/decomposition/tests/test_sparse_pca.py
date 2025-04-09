# Author: Vlad Niculae
# License: BSD 3 clause

import sys
import pytest

import numpy as np

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_allclose
from sklearn.utils.testing import if_safe_multiprocessing_with_blas

from sklearn.decomposition import SparsePCA, MiniBatchSparsePCA, PCA
from sklearn.utils import check_random_state


def generate_toy_data(n_components, n_samples, image_size, random_state=None):
    """
    Generate toy data for non-negative matrix factorization.
    
    Parameters
    ----------
    n_components : int
    Number of components or features to generate.
    n_samples : int
    Number of samples to generate.
    image_size : tuple of two ints
    Size of the images to generate.
    random_state : int, RandomState instance or None, optional (default=None)
    Determines random number generation for dataset creation. Pass an int
    for reproducible output across multiple function calls.
    """

    n_features = image_size[0] * image_size[1]

    rng = check_random_state(random_state)
    U = rng.randn(n_samples, n_components)
    V = rng.randn(n_components, n_features)

    centers = [(3, 3), (6, 7), (8, 1)]
    sz = [1, 2, 1]
    for k in range(n_components):
        img = np.zeros(image_size)
        xmin, xmax = centers[k][0] - sz[k], centers[k][0] + sz[k]
        ymin, ymax = centers[k][1] - sz[k], centers[k][1] + sz[k]
        img[xmin:xmax][:, ymin:ymax] = 1.0
        V[k, :] = img.ravel()

    # Y is defined by : Y = UV + noise
    Y = np.dot(U, V)
    Y += 0.1 * rng.randn(Y.shape[0], Y.shape[1])  # Add noise
    return Y, U, V

# SparsePCA can be a bit slow. To avoid having test times go up, we
# test different aspects of the code in the same test


def test_correct_shapes():
    """
    Test the shapes of the components and transformed data produced by SparsePCA.
    
    This function tests the `SparsePCA` class to ensure that it correctly
    fits and transforms input data `X`. The `SparsePCA` object is initialized
    with different numbers of components and used to fit the data. The shapes
    of the resulting components and transformed data are then verified.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `fit_transform`: Fits the
    """

    rng = np.random.RandomState(0)
    X = rng.randn(12, 10)
    spca = SparsePCA(n_components=8, random_state=rng)
    U = spca.fit_transform(X)
    assert_equal(spca.components_.shape, (8, 10))
    assert_equal(U.shape, (12, 8))
    # test overcomplete decomposition
    spca = SparsePCA(n_components=13, random_state=rng)
    U = spca.fit_transform(X)
    assert_equal(spca.components_.shape, (13, 10))
    assert_equal(U.shape, (12, 13))


def test_fit_transform():
    """
    Test the fit_transform method of SparsePCA using both 'lars' and 'cd' methods.
    
    This function generates toy data using `generate_toy_data` with specific parameters. It then fits two instances of SparsePCA: one using the 'lars' method and another using the 'cd' method. The alpha parameter is set to 1, indicating the regularization strength. The components_ attribute from both models are compared to ensure they produce similar results.
    
    Parameters:
    None
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=0)
    spca_lars.fit(Y)

    # Test that CD gives similar results
    spca_lasso = SparsePCA(n_components=3, method='cd', random_state=0,
                           alpha=alpha)
    spca_lasso.fit(Y)
    assert_array_almost_equal(spca_lasso.components_, spca_lars.components_)


@if_safe_multiprocessing_with_blas
def test_fit_transform_parallel():
    """
    Fit and transform a dataset using Sparse PCA with the LARS algorithm in parallel.
    
    This function generates a toy dataset, fits a SparsePCA model using the LARS algorithm with a specified alpha value, and then transforms the dataset. It also tests the functionality of fitting and transforming the dataset in parallel using multiple CPUs.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `generate_toy_data`: Generates a synthetic dataset.
    - `SparsePCA`: Fits and
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=0)
    spca_lars.fit(Y)
    U1 = spca_lars.transform(Y)
    # Test multiple CPUs
    spca = SparsePCA(n_components=3, n_jobs=2, method='lars', alpha=alpha,
                     random_state=0).fit(Y)
    U2 = spca.transform(Y)
    assert not np.all(spca_lars.components_ == 0)
    assert_array_almost_equal(U1, U2)


def test_transform_nan():
    """
    Test that SparsePCA handles zero features in all samples without returning NaN values.
    
    This function tests the `SparsePCA` class from scikit-learn by generating a toy dataset with a wide array of features. It sets one feature to zero across all samples and fits the `SparsePCA` model to this data. The function asserts that the transformed output does not contain any NaN values.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `generate_toy_data
    """

    # Test that SparsePCA won't return NaN when there is 0 feature in all
    # samples.
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    Y[:, 0] = 0
    estimator = SparsePCA(n_components=8)
    assert not np.any(np.isnan(estimator.fit_transform(Y)))


def test_fit_transform_tall():
    """
    Fit and transform a tall array using SparsePCA with different methods.
    
    This function generates a tall array of toy data and fits a SparsePCA model
    using both the 'lars' and 'cd' methods. It then compares the transformed
    results from both methods to ensure they are almost equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `generate_toy_data`: Generates the toy data used for fitting the model.
    - `Sparse
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 65, (8, 8), random_state=rng)  # tall array
    spca_lars = SparsePCA(n_components=3, method='lars', random_state=rng)
    U1 = spca_lars.fit_transform(Y)
    spca_lasso = SparsePCA(n_components=3, method='cd', random_state=rng)
    U2 = spca_lasso.fit(Y).transform(Y)
    assert_array_almost_equal(U1, U2)


def test_initialization():
    """
    Initialize and fit a SparsePCA model with custom initializations.
    
    This function initializes a SparsePCA model using specified initial
    matrices `U_init` and `V_init`. It then fits the model to a randomly
    generated dataset and checks if the components of the fitted model are
    normalized versions of the initial `V_init` matrix.
    
    Parameters:
    None (This function uses predefined random states and matrices).
    
    Returns:
    None (The function asserts the correctness of the model's
    """

    rng = np.random.RandomState(0)
    U_init = rng.randn(5, 3)
    V_init = rng.randn(3, 4)
    model = SparsePCA(n_components=3, U_init=U_init, V_init=V_init, max_iter=0,
                      random_state=rng)
    model.fit(rng.randn(5, 4))
    assert_allclose(model.components_,
                    V_init / np.linalg.norm(V_init, axis=1)[:, None])


def test_mini_batch_correct_shapes():
    """
    Test the MiniBatchSparsePCA class for correct shape of components and transformed data.
    
    This function tests the MiniBatchSparsePCA class by fitting it to a randomly generated dataset and verifying that the shapes of the learned components and the transformed data match the expected dimensions. The function creates a random dataset `X` with 12 samples and 10 features. It then fits the MiniBatchSparsePCA model with different numbers of components (8 and 13) to this data and checks that the
    """

    rng = np.random.RandomState(0)
    X = rng.randn(12, 10)
    pca = MiniBatchSparsePCA(n_components=8, random_state=rng)
    U = pca.fit_transform(X)
    assert_equal(pca.components_.shape, (8, 10))
    assert_equal(U.shape, (12, 8))
    # test overcomplete decomposition
    pca = MiniBatchSparsePCA(n_components=13, random_state=rng)
    U = pca.fit_transform(X)
    assert_equal(pca.components_.shape, (13, 10))
    assert_equal(U.shape, (12, 13))


# XXX: test always skipped
@pytest.mark.skipif(True, reason="skipping mini_batch_fit_transform.")
def test_mini_batch_fit_transform():
    """
    Test the fit_transform method of MiniBatchSparsePCA.
    
    This function evaluates the `fit_transform` method of the `MiniBatchSparsePCA`
    class by comparing the results obtained with and without parallel processing.
    It also compares the results obtained using the LARS and Coordinate Descent
    methods.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `generate_toy_data`: Generates toy data for testing.
    - `MiniBatchSparsePCA`: Fits
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = MiniBatchSparsePCA(n_components=3, random_state=0,
                                   alpha=alpha).fit(Y)
    U1 = spca_lars.transform(Y)
    # Test multiple CPUs
    if sys.platform == 'win32':  # fake parallelism for win32
        import sklearn.utils._joblib.parallel as joblib_par
        _mp = joblib_par.multiprocessing
        joblib_par.multiprocessing = None
        try:
            spca = MiniBatchSparsePCA(n_components=3, n_jobs=2, alpha=alpha,
                                      random_state=0)
            U2 = spca.fit(Y).transform(Y)
        finally:
            joblib_par.multiprocessing = _mp
    else:  # we can efficiently use parallelism
        spca = MiniBatchSparsePCA(n_components=3, n_jobs=2, alpha=alpha,
                                  random_state=0)
        U2 = spca.fit(Y).transform(Y)
    assert not np.all(spca_lars.components_ == 0)
    assert_array_almost_equal(U1, U2)
    # Test that CD gives similar results
    spca_lasso = MiniBatchSparsePCA(n_components=3, method='cd', alpha=alpha,
                                    random_state=0).fit(Y)
    assert_array_almost_equal(spca_lasso.components_, spca_lars.components_)


def test_scaling_fit_transform():
    """
    Test the scaling of fit_transform and transform methods for SparsePCA using the 'lars' method.
    
    This function evaluates the consistency between the transformed training data and a subset of the transformed test data using the SparsePCA model with the 'lars' method. The `fit_transform` method is applied to the entire dataset to obtain the transformed training data, while the `transform` method is applied to a subset of the dataset to obtain the transformed test data. The function asserts that the first component of
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 1000, (8, 8), random_state=rng)
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=rng)
    results_train = spca_lars.fit_transform(Y)
    results_test = spca_lars.transform(Y[:10])
    assert_allclose(results_train[0], results_test[0])


def test_pca_vs_spca():
    """
    Test the equivalence of PCA and SparsePCA.
    
    This function compares the results of Principal Component Analysis (PCA) and
    Sparse Principal Component Analysis (SparsePCA) on toy data. It generates
    two sets of data `Y` and `Z` using the `generate_toy_data` function. The PCA
    is performed on `Y` and `Z`, while SparsePCA is only performed on `Y`. The
    transformed results from both methods are then compared to ensure they
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 1000, (8, 8), random_state=rng)
    Z, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)
    spca = SparsePCA(alpha=0, ridge_alpha=0, n_components=2)
    pca = PCA(n_components=2)
    pca.fit(Y)
    spca.fit(Y)
    results_test_pca = pca.transform(Z)
    results_test_spca = spca.transform(Z)
    assert_allclose(np.abs(spca.components_.dot(pca.components_.T)),
                    np.eye(2), atol=1e-5)
    results_test_pca *= np.sign(results_test_pca[0, :])
    results_test_spca *= np.sign(results_test_spca[0, :])
    assert_allclose(results_test_pca, results_test_spca)


@pytest.mark.parametrize("spca", [SparsePCA, MiniBatchSparsePCA])
def test_spca_deprecation_warning(spca):
    """
    Tests the deprecation warning for the 'normalize_components' parameter in the `spca` function.
    
    This function verifies that a deprecation warning is raised when the `normalize_components` parameter is set to True in the `spca` function. The warning message should match the expected deprecation warning message.
    
    Parameters:
    spca (function): The `spca` function to be tested.
    
    Returns:
    None: This function does not return any value. It raises a deprecation
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)

    warn_msg = "'normalize_components' has been deprecated in 0.22"
    with pytest.warns(DeprecationWarning, match=warn_msg):
        spca(normalize_components=True).fit(Y)


@pytest.mark.parametrize("spca", [SparsePCA, MiniBatchSparsePCA])
def test_spca_error_unormalized_components(spca):
    """
    Test that SPCA raises an error when normalize_components is set to False.
    
    This function checks if SPCA raises a NotImplementedError when
    normalize_components is set to False. It uses the `generate_toy_data`
    function to create synthetic data and then attempts to fit the SPCA model
    with normalize_components set to False, expecting an error to be raised.
    
    Parameters:
    -----------
    spca : object
    The SPCA (Sparse Principal Component Analysis) object to be
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)

    err_msg = "normalize_components=False is not supported starting "
    with pytest.raises(NotImplementedError, match=err_msg):
        spca(normalize_components=False).fit(Y)
