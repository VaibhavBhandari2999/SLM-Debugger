import numpy as np
import scipy.sparse as sp
import pytest

from sklearn.utils.testing import (assert_array_almost_equal, assert_less,
                                   assert_equal, assert_not_equal,
                                   assert_raises, assert_allclose)

from sklearn.decomposition import PCA, KernelPCA
from sklearn.datasets import make_circles
from sklearn.linear_model import Perceptron
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics.pairwise import rbf_kernel


def test_kernel_pca():
    """
    Test KernelPCA with various kernels and eigen solvers.
    
    This function tests the `KernelPCA` class with different kernels and eigen solvers on randomly generated data. It ensures that the transformation of fit data and new data is consistent and that the inverse transformation works correctly when specified.
    
    Parameters:
    - X_fit (numpy.ndarray): The fit data used for training the model.
    - X_pred (numpy.ndarray): The new data to be transformed using the trained model.
    
    Kernels tested:
    """

    rng = np.random.RandomState(0)
    X_fit = rng.random_sample((5, 4))
    X_pred = rng.random_sample((2, 4))

    def histogram(x, y, **kwargs):
        """
        Generates a histogram using the minimum value between two arrays.
        
        This function calculates the histogram by summing up the minimum values
        between corresponding elements of two input arrays `x` and `y`.
        
        Parameters:
        -----------
        x : array-like
        The first input array.
        y : array-like
        The second input array.
        
        Returns:
        --------
        int
        The sum of the minimum values between corresponding elements of `x`
        and `y`.
        
        Notes
        """

        # Histogram kernel implemented as a callable.
        assert_equal(kwargs, {})    # no kernel_params that we didn't ask for
        return np.minimum(x, y).sum()

    for eigen_solver in ("auto", "dense", "arpack"):
        for kernel in ("linear", "rbf", "poly", histogram):
            # histogram kernel produces singular matrix inside linalg.solve
            # XXX use a least-squares approximation?
            inv = not callable(kernel)

            # transform fit data
            kpca = KernelPCA(4, kernel=kernel, eigen_solver=eigen_solver,
                             fit_inverse_transform=inv)
            X_fit_transformed = kpca.fit_transform(X_fit)
            X_fit_transformed2 = kpca.fit(X_fit).transform(X_fit)
            assert_array_almost_equal(np.abs(X_fit_transformed),
                                      np.abs(X_fit_transformed2))

            # non-regression test: previously, gamma would be 0 by default,
            # forcing all eigenvalues to 0 under the poly kernel
            assert_not_equal(X_fit_transformed.size, 0)

            # transform new data
            X_pred_transformed = kpca.transform(X_pred)
            assert_equal(X_pred_transformed.shape[1],
                         X_fit_transformed.shape[1])

            # inverse transform
            if inv:
                X_pred2 = kpca.inverse_transform(X_pred_transformed)
                assert_equal(X_pred2.shape, X_pred.shape)


def test_kernel_pca_invalid_parameters():
    assert_raises(ValueError, KernelPCA, 10, fit_inverse_transform=True,
                  kernel='precomputed')


def test_kernel_pca_consistent_transform():
    """
    Test that the transform method is consistent with a new fit.
    
    This function checks if the `transform` method of the `KernelPCA`
    class returns the same result when applied to an unchanged dataset
    (`X`) and a modified version of the dataset where only one column
    has been altered (`X_copy`). The `KernelPCA` object is first fitted
    to the original dataset `X`. The `transform` method is then called
    on both `X` and `
    """

    # X_fit_ needs to retain the old, unmodified copy of X
    state = np.random.RandomState(0)
    X = state.rand(10, 10)
    kpca = KernelPCA(random_state=state).fit(X)
    transformed1 = kpca.transform(X)

    X_copy = X.copy()
    X[:, 0] = 666
    transformed2 = kpca.transform(X_copy)
    assert_array_almost_equal(transformed1, transformed2)


def test_kernel_pca_deterministic_output():
    """
    Test deterministic output of KernelPCA.
    
    This function checks if the `KernelPCA` transformation produces consistent
    results across multiple runs when using the same random state and
    eigen_solver. It iterates over 20 trials, each time fitting and transforming
    a randomly generated dataset with `KernelPCA`, and asserts that the output
    is identical across all trials.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `KernelPCA`: Applies kernel
    """

    rng = np.random.RandomState(0)
    X = rng.rand(10, 10)
    eigen_solver = ('arpack', 'dense')

    for solver in eigen_solver:
        transformed_X = np.zeros((20, 2))
        for i in range(20):
            kpca = KernelPCA(n_components=2, eigen_solver=solver,
                             random_state=rng)
            transformed_X[i, :] = kpca.fit_transform(X)[0]
        assert_allclose(
            transformed_X, np.tile(transformed_X[0, :], 20).reshape(20, 2))


def test_kernel_pca_sparse():
    """
    Test KernelPCA with sparse input.
    
    This function tests the `KernelPCA` class on sparse input data using different kernels and eigen solvers. It ensures that the transformation of both fit and new data is consistent regardless of whether the `fit` method is called separately or within the `fit_transform` method.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `KernelPCA`: The main class used for performing kernel PCA.
    - `fit_transform`: Method
    """

    rng = np.random.RandomState(0)
    X_fit = sp.csr_matrix(rng.random_sample((5, 4)))
    X_pred = sp.csr_matrix(rng.random_sample((2, 4)))

    for eigen_solver in ("auto", "arpack"):
        for kernel in ("linear", "rbf", "poly"):
            # transform fit data
            kpca = KernelPCA(4, kernel=kernel, eigen_solver=eigen_solver,
                             fit_inverse_transform=False)
            X_fit_transformed = kpca.fit_transform(X_fit)
            X_fit_transformed2 = kpca.fit(X_fit).transform(X_fit)
            assert_array_almost_equal(np.abs(X_fit_transformed),
                                      np.abs(X_fit_transformed2))

            # transform new data
            X_pred_transformed = kpca.transform(X_pred)
            assert_equal(X_pred_transformed.shape[1],
                         X_fit_transformed.shape[1])

            # inverse transform
            # X_pred2 = kpca.inverse_transform(X_pred_transformed)
            # assert_equal(X_pred2.shape, X_pred.shape)


def test_kernel_pca_linear_kernel():
    """
    Test KernelPCA with linear kernel.
    
    This function verifies that KernelPCA with a linear kernel produces the same projection as PCA when applied to the same dataset. It fits the first four principal components using both KernelPCA and PCA, and then compares the absolute values of the transformed data from both methods. The comparison is done using `assert_array_almost_equal` to ensure the results are nearly equal, considering numerical precision issues.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    """

    rng = np.random.RandomState(0)
    X_fit = rng.random_sample((5, 4))
    X_pred = rng.random_sample((2, 4))

    # for a linear kernel, kernel PCA should find the same projection as PCA
    # modulo the sign (direction)
    # fit only the first four components: fifth is near zero eigenvalue, so
    # can be trimmed due to roundoff error
    assert_array_almost_equal(
        np.abs(KernelPCA(4).fit(X_fit).transform(X_pred)),
        np.abs(PCA(4).fit(X_fit).transform(X_pred)))


def test_kernel_pca_n_components():
    """
    Test the `KernelPCA` class with different `n_components` values.
    
    This function tests the `KernelPCA` class by fitting and transforming
    data with varying numbers of components (`n_components`). It uses two
    different methods for computing eigenvalues: 'dense' and 'arpack'. The
    function generates random samples for both fitting and predicting data,
    and checks that the transformed predictions have the expected shape.
    
    Parameters:
    None
    
    Returns:
    None
    """

    rng = np.random.RandomState(0)
    X_fit = rng.random_sample((5, 4))
    X_pred = rng.random_sample((2, 4))

    for eigen_solver in ("dense", "arpack"):
        for c in [1, 2, 4]:
            kpca = KernelPCA(n_components=c, eigen_solver=eigen_solver)
            shape = kpca.fit(X_fit).transform(X_pred).shape

            assert_equal(shape, (2, c))


def test_remove_zero_eig():
    """
    Test the behavior of the `remove_zero_eig` parameter in KernelPCA.
    
    This function evaluates the impact of setting `remove_zero_eig` to True or False on the shape of the transformed data matrix `Xt`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Summary:
    The function tests the `KernelPCA` class with different configurations of `n_components` and `remove_zero_eig`. It verifies that when `remove_zero_eig` is True (default
    """

    X = np.array([[1 - 1e-30, 1], [1, 1], [1, 1 - 1e-20]])

    # n_components=None (default) => remove_zero_eig is True
    kpca = KernelPCA()
    Xt = kpca.fit_transform(X)
    assert_equal(Xt.shape, (3, 0))

    kpca = KernelPCA(n_components=2)
    Xt = kpca.fit_transform(X)
    assert_equal(Xt.shape, (3, 2))

    kpca = KernelPCA(n_components=2, remove_zero_eig=True)
    Xt = kpca.fit_transform(X)
    assert_equal(Xt.shape, (3, 0))


def test_leave_zero_eig():
    """This test checks that fit().transform() returns the same result as
    fit_transform() in case of non-removed zero eigenvalue.
    Non-regression test for issue #12141 (PR #12143)"""
    X_fit = np.array([[1, 1], [0, 0]])

    # Assert that even with all np warnings on, there is no div by zero warning
    with pytest.warns(None) as record:
        with np.errstate(all='warn'):
            k = KernelPCA(n_components=2, remove_zero_eig=False,
                          eigen_solver="dense")
            # Fit, then transform
            A = k.fit(X_fit).transform(X_fit)
            # Do both at once
            B = k.fit_transform(X_fit)
            # Compare
            assert_array_almost_equal(np.abs(A), np.abs(B))

    for w in record:
        # There might be warnings about the kernel being badly conditioned,
        # but there should not be warnings about division by zero.
        # (Numpy division by zero warning can have many message variants, but
        # at least we know that it is a RuntimeWarning so lets check only this)
        assert not issubclass(w.category, RuntimeWarning)


def test_kernel_pca_precomputed():
    """
    Test KernelPCA with precomputed kernel.
    
    This function tests the `KernelPCA` class with the 'precomputed' kernel
    on both training and prediction data. It compares the results of fitting
    and transforming the data using different methods and ensures that the
    outputs are almost equal.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `np.random.RandomState`: To generate random sample data for testing.
    - `KernelPCA`: Class from
    """

    rng = np.random.RandomState(0)
    X_fit = rng.random_sample((5, 4))
    X_pred = rng.random_sample((2, 4))

    for eigen_solver in ("dense", "arpack"):
        X_kpca = KernelPCA(4, eigen_solver=eigen_solver).\
            fit(X_fit).transform(X_pred)
        X_kpca2 = KernelPCA(
            4, eigen_solver=eigen_solver, kernel='precomputed').fit(
                np.dot(X_fit, X_fit.T)).transform(np.dot(X_pred, X_fit.T))

        X_kpca_train = KernelPCA(
            4, eigen_solver=eigen_solver,
            kernel='precomputed').fit_transform(np.dot(X_fit, X_fit.T))
        X_kpca_train2 = KernelPCA(
            4, eigen_solver=eigen_solver, kernel='precomputed').fit(
                np.dot(X_fit, X_fit.T)).transform(np.dot(X_fit, X_fit.T))

        assert_array_almost_equal(np.abs(X_kpca),
                                  np.abs(X_kpca2))

        assert_array_almost_equal(np.abs(X_kpca_train),
                                  np.abs(X_kpca_train2))


def test_kernel_pca_invalid_kernel():
    """
    Test that an error is raised when an invalid kernel is specified.
    
    This function checks if a `ValueError` is raised when attempting to fit
    a `KernelPCA` instance with an invalid kernel. The `KernelPCA` class is
    initialized with a 'tototiti' kernel, which is not a valid kernel type,
    and the `fit` method is called on a random sample of shape (2, 4).
    The function asserts that a `ValueError`
    """

    rng = np.random.RandomState(0)
    X_fit = rng.random_sample((2, 4))
    kpca = KernelPCA(kernel="tototiti")
    assert_raises(ValueError, kpca.fit, X_fit)


# 0.23. warning about tol not having its correct default value.
@pytest.mark.filterwarnings('ignore:max_iter and tol parameters have been')
def test_gridsearch_pipeline():
    """
    Test grid search on a pipeline.
    
    This function evaluates the ability to perform a grid search to optimize
    hyperparameters for separating circles using a perceptron model after
    applying Kernel PCA. The function creates synthetic data using `make_circles`,
    applies a pipeline consisting of Kernel PCA and a Perceptron, and performs
    a grid search over different values of the 'gamma' parameter for Kernel PCA.
    The goal is to achieve a perfect separation (score of 1) by
    """

    # Test if we can do a grid-search to find parameters to separate
    # circles with a perceptron model.
    X, y = make_circles(n_samples=400, factor=.3, noise=.05,
                        random_state=0)
    kpca = KernelPCA(kernel="rbf", n_components=2)
    pipeline = Pipeline([("kernel_pca", kpca),
                         ("Perceptron", Perceptron(max_iter=5))])
    param_grid = dict(kernel_pca__gamma=2. ** np.arange(-2, 2))
    grid_search = GridSearchCV(pipeline, cv=3, param_grid=param_grid)
    grid_search.fit(X, y)
    assert_equal(grid_search.best_score_, 1)


# 0.23. warning about tol not having its correct default value.
@pytest.mark.filterwarnings('ignore:max_iter and tol parameters have been')
def test_gridsearch_pipeline_precomputed():
    """
    Test grid search on a pipeline with a precomputed kernel.
    
    This function evaluates the ability to perform a grid search to optimize
    parameters for separating circles using a perceptron model with a precomputed
    kernel. The process involves creating a dataset of circles, applying a
    precomputed kernel PCA transformation, and then fitting a perceptron model
    through a pipeline. The grid search is conducted over a range of maximum
    iterations for the perceptron, and the best score achieved is
    """

    # Test if we can do a grid-search to find parameters to separate
    # circles with a perceptron model using a precomputed kernel.
    X, y = make_circles(n_samples=400, factor=.3, noise=.05,
                        random_state=0)
    kpca = KernelPCA(kernel="precomputed", n_components=2)
    pipeline = Pipeline([("kernel_pca", kpca),
                         ("Perceptron", Perceptron(max_iter=5))])
    param_grid = dict(Perceptron__max_iter=np.arange(1, 5))
    grid_search = GridSearchCV(pipeline, cv=3, param_grid=param_grid)
    X_kernel = rbf_kernel(X, gamma=2.)
    grid_search.fit(X_kernel, y)
    assert_equal(grid_search.best_score_, 1)


# 0.23. warning about tol not having its correct default value.
@pytest.mark.filterwarnings('ignore:max_iter and tol parameters have been')
def test_nested_circles():
    """
    Test the linear separability of 2D nested circles data after applying Kernel Principal Component Analysis (KPCA) with an RBF kernel.
    
    This function evaluates the linear separability of the 2D nested circles dataset before and after applying KPCA. Initially, it checks if the circles are not linearly separable in their original 2D space. Then, it projects the data into a lower-dimensional space using KPCA with an RBF kernel. Finally, it verifies if the transformed data
    """

    # Test the linear separability of the first 2D KPCA transform
    X, y = make_circles(n_samples=400, factor=.3, noise=.05,
                        random_state=0)

    # 2D nested circles are not linearly separable
    train_score = Perceptron(max_iter=5).fit(X, y).score(X, y)
    assert_less(train_score, 0.8)

    # Project the circles data into the first 2 components of a RBF Kernel
    # PCA model.
    # Note that the gamma value is data dependent. If this test breaks
    # and the gamma value has to be updated, the Kernel PCA example will
    # have to be updated too.
    kpca = KernelPCA(kernel="rbf", n_components=2,
                     fit_inverse_transform=True, gamma=2.)
    X_kpca = kpca.fit_transform(X)

    # The data is perfectly linearly separable in that space
    train_score = Perceptron(max_iter=5).fit(X_kpca, y).score(X_kpca, y)
    assert_equal(train_score, 1.0)
