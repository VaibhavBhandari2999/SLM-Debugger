# Author: Vlad Niculae
# License: BSD 3 clause

import sys
import pytest

import numpy as np

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_allclose
from sklearn.utils.testing import assert_warns_message
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


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_correct_shapes(norm_comp):
    """
    Test the shapes of the components and transformed data produced by SparsePCA.
    
    This function tests the `SparsePCA` class from scikit-learn to ensure that
    the shapes of the components and transformed data are correct for both
    standard and overcomplete decompositions. The function uses a random
    generator to create input data and fits the model with specified
    parameters. It then checks the shapes of the components and the transformed
    data against expected values.
    
    Parameters:
    norm
    """

    rng = np.random.RandomState(0)
    X = rng.randn(12, 10)
    spca = SparsePCA(n_components=8, random_state=rng,
                     normalize_components=norm_comp)
    U = spca.fit_transform(X)
    assert_equal(spca.components_.shape, (8, 10))
    assert_equal(U.shape, (12, 8))
    # test overcomplete decomposition
    spca = SparsePCA(n_components=13, random_state=rng,
                     normalize_components=norm_comp)
    U = spca.fit_transform(X)
    assert_equal(spca.components_.shape, (13, 10))
    assert_equal(U.shape, (12, 13))


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_fit_transform(norm_comp):
    """
    Fit and transform the input data using Sparse Principal Component Analysis (SparsePCA).
    
    This function fits a SparsePCA model to the input data `Y` using either the LARS or Coordinate Descent (CD) methods. It then transforms the data using the learned components.
    
    Parameters:
    - norm_comp (bool): Whether to normalize the components of the SparsePCA model.
    
    Returns:
    - None: The function does not return any value. It modifies the `spca_lars` and
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=0, normalize_components=norm_comp)
    spca_lars.fit(Y)

    # Test that CD gives similar results
    spca_lasso = SparsePCA(n_components=3, method='cd', random_state=0,
                           alpha=alpha, normalize_components=norm_comp)
    spca_lasso.fit(Y)
    assert_array_almost_equal(spca_lasso.components_, spca_lars.components_)


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
@if_safe_multiprocessing_with_blas
def test_fit_transform_parallel(norm_comp):
    """
    Fit and transform a dataset using Sparse PCA with LARS algorithm in parallel.
    
    This function fits a SparsePCA model on a given dataset `Y` using the LARS
    algorithm and then transforms the same dataset. The transformation is
    performed in parallel across multiple CPU cores.
    
    Parameters:
    -----------
    norm_comp : bool
    Whether to normalize the components of the SparsePCA model.
    
    Returns:
    --------
    U1, U2 : numpy.ndarray
    The transformed data
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=0, normalize_components=norm_comp)
    spca_lars.fit(Y)
    U1 = spca_lars.transform(Y)
    # Test multiple CPUs
    spca = SparsePCA(n_components=3, n_jobs=2, method='lars', alpha=alpha,
                     random_state=0, normalize_components=norm_comp).fit(Y)
    U2 = spca.transform(Y)
    assert not np.all(spca_lars.components_ == 0)
    assert_array_almost_equal(U1, U2)


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_transform_nan(norm_comp):
    """
    Test that SparsePCA handles zero features correctly.
    
    This function verifies that SparsePCA does not return NaN values when
    there are zero features present in all samples of the input data.
    
    Parameters:
    -----------
    norm_comp : bool
    Indicates whether the components should be normalized or not.
    
    Returns:
    --------
    None
    
    The function uses the following key elements:
    - `generate_toy_data`: Generates synthetic data for testing.
    - `SparsePCA`: Applies Sparse Principal
    """

    # Test that SparsePCA won't return NaN when there is 0 feature in all
    # samples.
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    Y[:, 0] = 0
    estimator = SparsePCA(n_components=8, normalize_components=norm_comp)
    assert not np.any(np.isnan(estimator.fit_transform(Y)))


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_fit_transform_tall(norm_comp):
    """
    Fit and transform a tall array using SparsePCA with different methods.
    
    This function generates a tall array of toy data and fits a SparsePCA model
    using both the 'lars' and 'cd' methods. The transformed components are then
    compared to ensure consistency.
    
    Parameters:
    norm_comp (bool): Whether to normalize the components of the SparsePCA model.
    
    Returns:
    None: The function asserts that the transformed components from both methods
    are almost equal, but does
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 65, (8, 8), random_state=rng)  # tall array
    spca_lars = SparsePCA(n_components=3, method='lars',
                          random_state=rng, normalize_components=norm_comp)
    U1 = spca_lars.fit_transform(Y)
    spca_lasso = SparsePCA(n_components=3, method='cd',
                           random_state=rng, normalize_components=norm_comp)
    U2 = spca_lasso.fit(Y).transform(Y)
    assert_array_almost_equal(U1, U2)


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_initialization(norm_comp):
    """
    Initialize and fit a SparsePCA model with given initial components.
    
    This function initializes a SparsePCA model using specified initial
    components `U_init` and `V_init`. It then fits the model to a randomly
    generated dataset and checks the normalization of the components based on
    the `norm_comp` parameter.
    
    Parameters:
    -----------
    norm_comp : bool
    Determines whether the components should be normalized (True) or not
    (False).
    
    Returns:
    --------
    """

    rng = np.random.RandomState(0)
    U_init = rng.randn(5, 3)
    V_init = rng.randn(3, 4)
    model = SparsePCA(n_components=3, U_init=U_init, V_init=V_init, max_iter=0,
                      random_state=rng, normalize_components=norm_comp)
    model.fit(rng.randn(5, 4))
    if norm_comp:
        assert_allclose(model.components_,
                        V_init / np.linalg.norm(V_init, axis=1)[:, None])
    else:
        assert_allclose(model.components_, V_init)


@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_mini_batch_correct_shapes(norm_comp):
    """
    Test the MiniBatchSparsePCA class for correct shape of components and transformed data.
    
    This function tests the MiniBatchSparsePCA class by fitting it to a random dataset and checking the shapes of the resulting components and transformed data. It also verifies that the class can handle an overcomplete decomposition.
    
    Parameters:
    norm_comp (bool): Whether to normalize the components or not.
    
    Returns:
    None: The function asserts the correctness of the shapes of the components and transformed data.
    
    Functions Used:
    """

    rng = np.random.RandomState(0)
    X = rng.randn(12, 10)
    pca = MiniBatchSparsePCA(n_components=8, random_state=rng,
                             normalize_components=norm_comp)
    U = pca.fit_transform(X)
    assert_equal(pca.components_.shape, (8, 10))
    assert_equal(U.shape, (12, 8))
    # test overcomplete decomposition
    pca = MiniBatchSparsePCA(n_components=13, random_state=rng,
                             normalize_components=norm_comp)
    U = pca.fit_transform(X)
    assert_equal(pca.components_.shape, (13, 10))
    assert_equal(U.shape, (12, 13))


# XXX: test always skipped
@pytest.mark.skipif(True, reason="skipping mini_batch_fit_transform.")
@pytest.mark.filterwarnings("ignore:normalize_components")
@pytest.mark.parametrize("norm_comp", [False, True])
def test_mini_batch_fit_transform(norm_comp):
    """
    Fit and transform a dataset using MiniBatchSparsePCA.
    
    This function fits a MiniBatchSparsePCA model to the given data and
    transforms the data using the learned components. It supports both
    parallel and non-parallel fitting, depending on the operating system.
    
    Parameters:
    -----------
    norm_comp : bool
    Whether to normalize the components of the sparse PCA.
    
    Returns:
    --------
    U1, U2 : numpy arrays
    Transformed data using the components learned
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)  # wide array
    spca_lars = MiniBatchSparsePCA(n_components=3, random_state=0,
                                   alpha=alpha,
                                   normalize_components=norm_comp).fit(Y)
    U1 = spca_lars.transform(Y)
    # Test multiple CPUs
    if sys.platform == 'win32':  # fake parallelism for win32
        import sklearn.utils._joblib.parallel as joblib_par
        _mp = joblib_par.multiprocessing
        joblib_par.multiprocessing = None
        try:
            spca = MiniBatchSparsePCA(n_components=3, n_jobs=2, alpha=alpha,
                                      random_state=0,
                                      normalize_components=norm_comp)
            U2 = spca.fit(Y).transform(Y)
        finally:
            joblib_par.multiprocessing = _mp
    else:  # we can efficiently use parallelism
        spca = MiniBatchSparsePCA(n_components=3, n_jobs=2, alpha=alpha,
                                  random_state=0,
                                  normalize_components=norm_comp)
        U2 = spca.fit(Y).transform(Y)
    assert not np.all(spca_lars.components_ == 0)
    assert_array_almost_equal(U1, U2)
    # Test that CD gives similar results
    spca_lasso = MiniBatchSparsePCA(n_components=3, method='cd', alpha=alpha,
                                    random_state=0,
                                    normalize_components=norm_comp).fit(Y)
    assert_array_almost_equal(spca_lasso.components_, spca_lars.components_)


def test_scaling_fit_transform():
    """
    Test the scaling and fit_transform methods of SparsePCA using the LARS algorithm.
    
    This function evaluates the consistency of the transformation by comparing
    the results obtained from fitting and transforming the entire dataset with
    those obtained from fitting the full dataset and then transforming a subset
    of it. The SparsePCA object is initialized with the following parameters:
    - n_components: 3
    - method: 'lars'
    - alpha: 1
    - random_state: 0
    """

    alpha = 1
    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 1000, (8, 8), random_state=rng)
    spca_lars = SparsePCA(n_components=3, method='lars', alpha=alpha,
                          random_state=rng, normalize_components=True)
    results_train = spca_lars.fit_transform(Y)
    results_test = spca_lars.transform(Y[:10])
    assert_allclose(results_train[0], results_test[0])


def test_pca_vs_spca():
    """
    Test the equivalence between PCA and SparsePCA.
    
    This function compares the results of Principal Component Analysis (PCA) and
    Sparse Principal Component Analysis (SparsePCA) on toy datasets. It generates
    two sets of data `Y` and `Z` using the `generate_toy_data` function. The PCA
    model is fitted to `Y` and then used to transform `Z`. Similarly, the SparsePCA
    model is fitted to `Y` and then used to transform
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 1000, (8, 8), random_state=rng)
    Z, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)
    spca = SparsePCA(alpha=0, ridge_alpha=0, n_components=2,
                     normalize_components=True)
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
    Tests the deprecation warning for the `spca` function when `normalize_components` is set to False.
    
    This function evaluates whether a deprecation warning is raised when the `spca` function is called with `normalize_components` set to False. The `spca` function is expected to fit the provided data `Y` and raise a DeprecationWarning with a specific message if `normalize_components` is not normalized.
    
    Parameters:
    spca (function): The spca function
    """

    rng = np.random.RandomState(0)
    Y, _, _ = generate_toy_data(3, 10, (8, 8), random_state=rng)
    warn_message = "normalize_components"
    assert_warns_message(DeprecationWarning, warn_message,
                         spca(normalize_components=False).fit, Y)
