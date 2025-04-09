# Important note for the deprecation cleaning of 0.20 :
# All the functions and classes of this file have been deprecated in 0.18.
# When you remove this file please remove the related files
# - 'sklearn/mixture/dpgmm.py'
# - 'sklearn/mixture/gmm.py'
# - 'sklearn/mixture/test_dpgmm.py'
import unittest
import copy
import sys

import pytest

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from scipy import stats
from sklearn import mixture
from sklearn.datasets.samples_generator import make_spd_matrix
from sklearn.utils.testing import (assert_true, assert_greater,
                                   assert_raise_message, assert_warns_message,
                                   ignore_warnings, assert_raises)
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.externals.six.moves import cStringIO as StringIO


rng = np.random.RandomState(0)


def test_sample_gaussian():
    """
    Test sample generation from mixture.sample_gaussian.
    
    This function tests the sample generation process from the `_sample_gaussian` method of the `mixture.gmm` module. It verifies that the generated samples match the expected mean and variance for different types of covariance matrices: diagonal, spherical, and full.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `_sample_gaussian`: Generates samples from a Gaussian distribution with specified mean (`mu`) and covariance (`cv
    """

    # Test sample generation from mixture.sample_gaussian where covariance
    # is diagonal, spherical and full

    n_features, n_samples = 2, 300
    axis = 1
    mu = rng.randint(10) * rng.rand(n_features)
    cv = (rng.rand(n_features) + 1.0) ** 2

    samples = mixture.gmm._sample_gaussian(
        mu, cv, covariance_type='diag', n_samples=n_samples)

    assert_true(np.allclose(samples.mean(axis), mu, atol=1.3))
    assert_true(np.allclose(samples.var(axis), cv, atol=1.5))

    # the same for spherical covariances
    cv = (rng.rand() + 1.0) ** 2
    samples = mixture.gmm._sample_gaussian(
        mu, cv, covariance_type='spherical', n_samples=n_samples)

    assert_true(np.allclose(samples.mean(axis), mu, atol=1.5))
    assert_true(np.allclose(
        samples.var(axis), np.repeat(cv, n_features), atol=1.5))

    # and for full covariances
    A = rng.randn(n_features, n_features)
    cv = np.dot(A.T, A) + np.eye(n_features)
    samples = mixture.gmm._sample_gaussian(
        mu, cv, covariance_type='full', n_samples=n_samples)
    assert_true(np.allclose(samples.mean(axis), mu, atol=1.3))
    assert_true(np.allclose(np.cov(samples), cv, atol=2.5))

    # Numerical stability check: in SciPy 0.12.0 at least, eigh may return
    # tiny negative values in its second return value.
    x = mixture.gmm._sample_gaussian(
        [0, 0], [[4, 3], [1, .1]], covariance_type='full', random_state=42)
    assert_true(np.isfinite(x).all())


def _naive_lmvnpdf_diag(X, mu, cv):
    """
    Computes the log multivariate normal probability density function (log MVN PDF) for a set of data points.
    
    Args:
    X (numpy.ndarray): Input data points with shape (n_samples, n_features).
    mu (numpy.ndarray): Mean values of the MVN distribution with shape (n_features,).
    cv (numpy.ndarray): Covariance matrix of the MVN distribution with shape (n_features, n_features).
    
    Returns:
    numpy.ndarray: Log MVN PDF values for
    """

    # slow and naive implementation of lmvnpdf
    ref = np.empty((len(X), len(mu)))
    stds = np.sqrt(cv)
    for i, (m, std) in enumerate(zip(mu, stds)):
        ref[:, i] = np.log(stats.norm.pdf(X, m, std)).sum(axis=1)
    return ref


def test_lmvnpdf_diag():
    """
    Test the correctness of the log multivariate normal probability density function (lmvnpdf) for diagonal covariance matrices.
    
    This function compares a slow and naive implementation of the log multivariate normal probability density function (lmvnpdf) with a vectorized version (mixture.lmvnpdf) to ensure their outputs are nearly identical.
    
    Parameters:
    -----------
    n_features : int
    The number of features (dimensions) in the data.
    n_components : int
    The
    """

    # test a slow and naive implementation of lmvnpdf and
    # compare it to the vectorized version (mixture.lmvnpdf) to test
    # for correctness
    n_features, n_components, n_samples = 2, 3, 10
    mu = rng.randint(10) * rng.rand(n_components, n_features)
    cv = (rng.rand(n_components, n_features) + 1.0) ** 2
    X = rng.randint(10) * rng.rand(n_samples, n_features)

    ref = _naive_lmvnpdf_diag(X, mu, cv)
    lpr = assert_warns_message(DeprecationWarning, "The function"
                             " log_multivariate_normal_density is "
                             "deprecated in 0.18 and will be removed in 0.20.",
                             mixture.log_multivariate_normal_density,
                             X, mu, cv, 'diag')
    assert_array_almost_equal(lpr, ref)


def test_lmvnpdf_spherical():
    """
    Test the log-likelihood of a multivariate normal distribution with spherical covariance.
    
    This function evaluates the log-likelihood of a given set of samples `X`
    under a multivariate normal distribution characterized by means `mu` and
    spherical covariances `spherecv`. The function uses both a custom `_naive_lmvnpdf_diag`
    implementation and the deprecated `log_multivariate_normal_density` function from the
    `mixture` module to compute the log-probability
    """

    n_features, n_components, n_samples = 2, 3, 10

    mu = rng.randint(10) * rng.rand(n_components, n_features)
    spherecv = rng.rand(n_components, 1) ** 2 + 1
    X = rng.randint(10) * rng.rand(n_samples, n_features)

    cv = np.tile(spherecv, (n_features, 1))
    reference = _naive_lmvnpdf_diag(X, mu, cv)
    lpr = assert_warns_message(DeprecationWarning, "The function"
                             " log_multivariate_normal_density is "
                             "deprecated in 0.18 and will be removed in 0.20.",
                             mixture.log_multivariate_normal_density,
                             X, mu, spherecv, 'spherical')
    assert_array_almost_equal(lpr, reference)

def test_lmvnpdf_full():
    """
    Computes the log probability density of a multivariate normal distribution.
    
    This function calculates the log probability density of a given set of samples
    under a multivariate normal distribution with specified means and covariance matrices.
    
    Parameters:
    -----------
    X : array-like, shape (n_samples, n_features)
    The data points for which the log probability density is computed.
    mu : array-like, shape (n_components, n_features)
    The mean vectors of the multivariate normal distributions.
    """

    n_features, n_components, n_samples = 2, 3, 10

    mu = rng.randint(10) * rng.rand(n_components, n_features)
    cv = (rng.rand(n_components, n_features) + 1.0) ** 2
    X = rng.randint(10) * rng.rand(n_samples, n_features)

    fullcv = np.array([np.diag(x) for x in cv])

    reference = _naive_lmvnpdf_diag(X, mu, cv)
    lpr = assert_warns_message(DeprecationWarning, "The function"
                             " log_multivariate_normal_density is "
                             "deprecated in 0.18 and will be removed in 0.20.",
                             mixture.log_multivariate_normal_density,
                             X, mu, fullcv, 'full')
    assert_array_almost_equal(lpr, reference)


def test_lvmpdf_full_cv_non_positive_definite():
    """
    Test log_multivariate_normal_density with full covariance matrix that is non-positive definite.
    
    This function tests the `log_multivariate_normal_density` function with a non-positive definite covariance matrix (`cv`). It verifies that an appropriate error message is raised when the covariance matrix is not valid.
    
    Parameters:
    - n_features (int): Number of features in the dataset.
    - n_samples (int): Number of samples in the dataset.
    - rng (numpy.random.Generator): Random number generator.
    """

    n_features, n_samples = 2, 10
    rng = np.random.RandomState(0)
    X = rng.randint(10) * rng.rand(n_samples, n_features)
    mu = np.mean(X, 0)
    cv = np.array([[[-1, 0], [0, 1]]])
    expected_message = "'covars' must be symmetric, positive-definite"
    assert_raise_message(ValueError, expected_message,
                         mixture.log_multivariate_normal_density,
                         X, mu, cv, 'full')


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_GMM_attributes():
    """
    Test the attributes of a Gaussian Mixture Model (GMM).
    
    This function initializes a GMM with specified parameters and verifies
    that the model's attributes are correctly set. It checks the number of
    components, covariance type, and ensures that the weights, means, and
    covariances are properly assigned.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `mixture.GMM`: Initializes the GMM with given parameters.
    -
    """

    n_components, n_features = 10, 4
    covariance_type = 'diag'
    g = mixture.GMM(n_components, covariance_type, random_state=rng)
    weights = rng.rand(n_components)
    weights = weights / weights.sum()
    means = rng.randint(-20, 20, (n_components, n_features))

    assert_true(g.n_components == n_components)
    assert_true(g.covariance_type == covariance_type)

    g.weights_ = weights
    assert_array_almost_equal(g.weights_, weights)
    g.means_ = means
    assert_array_almost_equal(g.means_, means)

    covars = (0.1 + 2 * rng.rand(n_components, n_features)) ** 2
    g.covars_ = covars
    assert_array_almost_equal(g.covars_, covars)
    assert_raises(ValueError, g._set_covars, [])
    assert_raises(ValueError, g._set_covars,
                  np.zeros((n_components - 2, n_features)))
    assert_raises(ValueError, mixture.GMM, n_components=20,
                  covariance_type='badcovariance_type')


class GMMTester():
    do_test_eval = True

    def _setUp(self):
        """
        Sets up the initial parameters for the Gaussian Mixture Model.
        
        This method initializes various parameters required for a Gaussian Mixture Model, including the number of components, weights, means, threshold, and covariance matrices for different types of covariance structures.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes Set:
        - n_components: The number of mixture components (int).
        - n_features: The number of features (int).
        - weights: The mixing weights for each component (
        """

        self.n_components = 10
        self.n_features = 4
        self.weights = rng.rand(self.n_components)
        self.weights = self.weights / self.weights.sum()
        self.means = rng.randint(-20, 20, (self.n_components, self.n_features))
        self.threshold = -0.5
        self.I = np.eye(self.n_features)
        self.covars = {
            'spherical': (0.1 + 2 * rng.rand(self.n_components,
                                             self.n_features)) ** 2,
            'tied': (make_spd_matrix(self.n_features, random_state=0)
                     + 5 * self.I),
            'diag': (0.1 + 2 * rng.rand(self.n_components,
                                        self.n_features)) ** 2,
            'full': np.array([make_spd_matrix(self.n_features, random_state=0)
                              + 5 * self.I for x in range(self.n_components)])}

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def test_eval(self):
        """
        Tests the evaluation of the model using score_samples.
        
        This function evaluates the model's log-likelihood and responsibilities
        for given data points. It ensures that the means and covariances are set
        correctly and that the responsibilities correctly identify the generated
        components.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `score_samples`: Computes the log-likelihood of X under the model and
        the posterior probabilities of the components.
        - `
        """

        if not self.do_test_eval:
            return  # DPGMM does not support setting the means and
        # covariances before fitting There is no way of fixing this
        # due to the variational parameters being more expressive than
        # covariance matrices
        g = self.model(n_components=self.n_components,
                       covariance_type=self.covariance_type, random_state=rng)
        # Make sure the means are far apart so responsibilities.argmax()
        # picks the actual component used to generate the observations.
        g.means_ = 20 * self.means
        g.covars_ = self.covars[self.covariance_type]
        g.weights_ = self.weights

        gaussidx = np.repeat(np.arange(self.n_components), 5)
        n_samples = len(gaussidx)
        X = rng.randn(n_samples, self.n_features) + g.means_[gaussidx]

        with ignore_warnings(category=DeprecationWarning):
            ll, responsibilities = g.score_samples(X)

        self.assertEqual(len(ll), n_samples)
        self.assertEqual(responsibilities.shape,
                         (n_samples, self.n_components))
        assert_array_almost_equal(responsibilities.sum(axis=1),
                                  np.ones(n_samples))
        assert_array_equal(responsibilities.argmax(axis=1), gaussidx)

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def test_sample(self, n=100):
        """
        Generates samples from a Gaussian Mixture Model.
        
        This function creates a Gaussian Mixture Model (GMM) using the specified number of components, covariance type, and other parameters. The means of the components are scaled by a factor of 20 to ensure that they are sufficiently far apart. The covariance matrices and weights are set according to the provided values. The function then generates `n` samples from this GMM and verifies that the shape of the generated samples matches the expected dimensions.
        """

        g = self.model(n_components=self.n_components,
                       covariance_type=self.covariance_type,
                       random_state=rng)
        # Make sure the means are far apart so responsibilities.argmax()
        # picks the actual component used to generate the observations.
        g.means_ = 20 * self.means
        g.covars_ = np.maximum(self.covars[self.covariance_type], 0.1)
        g.weights_ = self.weights

        with ignore_warnings(category=DeprecationWarning):
            samples = g.sample(n)
        self.assertEqual(samples.shape, (n, self.n_features))

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def test_train(self, params='wmc'):
        """
        Tests the training process of a Gaussian Mixture Model (GMM).
        
        This function initializes a GMM using predefined weights, means, and covariances.
        It then samples data from this GMM and trains the model iteratively to ensure
        the log-likelihood increases with each iteration.
        
        Parameters:
        - params (str): Specifies the parameters to be initialized during training.
        
        Returns:
        - None: The function asserts whether the log-likelihood increases appropriately during training.
        
        Key
        """

        g = mixture.GMM(n_components=self.n_components,
                        covariance_type=self.covariance_type)
        with ignore_warnings(category=DeprecationWarning):
            g.weights_ = self.weights
            g.means_ = self.means
            g.covars_ = 20 * self.covars[self.covariance_type]

        # Create a training set by sampling from the predefined distribution.
        with ignore_warnings(category=DeprecationWarning):
            X = g.sample(n_samples=100)
            g = self.model(n_components=self.n_components,
                           covariance_type=self.covariance_type,
                           random_state=rng, min_covar=1e-1,
                           n_iter=1, init_params=params)
            g.fit(X)

        # Do one training iteration at a time so we can keep track of
        # the log likelihood to make sure that it increases after each
        # iteration.
        trainll = []
        with ignore_warnings(category=DeprecationWarning):
            for _ in range(5):
                g.params = params
                g.init_params = ''
                g.fit(X)
                trainll.append(self.score(g, X))
            g.n_iter = 10
            g.init_params = ''
            g.params = params
            g.fit(X)  # finish fitting

        # Note that the log likelihood will sometimes decrease by a
        # very small amount after it has more or less converged due to
        # the addition of min_covar to the covariance (to prevent
        # underflow).  This is why the threshold is set to -0.5
        # instead of 0.
        with ignore_warnings(category=DeprecationWarning):
            delta_min = np.diff(trainll).min()
        self.assertTrue(
            delta_min > self.threshold,
            "The min nll increase is %f which is lower than the admissible"
            " threshold of %f, for model %s. The likelihoods are %s."
            % (delta_min, self.threshold, self.covariance_type, trainll))

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def test_train_degenerate(self, params='wmc'):
        """
        Trains a Gaussian Mixture Model (GMM) on degenerate data with zero values in some dimensions.
        
        Parameters:
        - params (str): The initialization parameters for the GMM. Default is 'wmc'.
        
        Returns:
        - None: This function does not return any value. It checks if the trained model's log likelihood is within an acceptable range.
        
        Important Functions:
        - `rng.randn`: Generates random numbers from a standard normal distribution.
        - `self.model`:
        """

        # Train on degenerate data with 0 in some dimensions
        # Create a training set by sampling from the predefined
        # distribution.
        X = rng.randn(100, self.n_features)
        X.T[1:] = 0
        g = self.model(n_components=2,
                       covariance_type=self.covariance_type,
                       random_state=rng, min_covar=1e-3, n_iter=5,
                       init_params=params)
        with ignore_warnings(category=DeprecationWarning):
            g.fit(X)
            trainll = g.score(X)
        self.assertTrue(np.sum(np.abs(trainll / 100 / X.shape[1])) < 5)

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def test_train_1d(self, params='wmc'):
        """
        Trains a Gaussian Mixture Model (GMM) on 1-dimensional data.
        
        This function generates a training set using a normal distribution and fits
        a GMM model to this data. The model's performance is evaluated based on the
        log-likelihood of the training data.
        
        Parameters:
        - params (str): Specifies the initialization parameters for the GMM.
        
        Returns:
        - None: The function does not return any value but modifies the GMM object in place.
        """

        # Train on 1-D data
        # Create a training set by sampling from the predefined
        # distribution.
        X = rng.randn(100, 1)
        # X.T[1:] = 0
        g = self.model(n_components=2,
                       covariance_type=self.covariance_type,
                       random_state=rng, min_covar=1e-7, n_iter=5,
                       init_params=params)
        with ignore_warnings(category=DeprecationWarning):
            g.fit(X)
            trainll = g.score(X)
            if isinstance(g, mixture.dpgmm._DPGMMBase):
                self.assertTrue(np.sum(np.abs(trainll / 100)) < 5)
            else:
                self.assertTrue(np.sum(np.abs(trainll / 100)) < 2)

    # This function tests the deprecated old GMM class
    @ignore_warnings(category=DeprecationWarning)
    def score(self, g, X):
        with ignore_warnings(category=DeprecationWarning):
            return g.score(X).sum()


class TestGMMWithSphericalCovars(unittest.TestCase, GMMTester):
    covariance_type = 'spherical'
    model = mixture.GMM
    setUp = GMMTester._setUp


class TestGMMWithDiagonalCovars(unittest.TestCase, GMMTester):
    covariance_type = 'diag'
    model = mixture.GMM
    setUp = GMMTester._setUp


class TestGMMWithTiedCovars(unittest.TestCase, GMMTester):
    covariance_type = 'tied'
    model = mixture.GMM
    setUp = GMMTester._setUp


class TestGMMWithFullCovars(unittest.TestCase, GMMTester):
    covariance_type = 'full'
    model = mixture.GMM
    setUp = GMMTester._setUp


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_multiple_init():
    """
    Tests the performance of multiple initializations in a Gaussian Mixture Model (GMM).
    
    This function evaluates the impact of using multiple initializations on the GMM's training process. It generates a dataset `X` with two clusters and fits a GMM model to this data. The function then compares the total log-likelihood scores obtained from fitting the model once (`train1`) and fitting it five times with multiple initializations (`train2`). The assertion ensures that using multiple initializations does not significantly
    """

    # Test that multiple inits does not much worse than a single one
    X = rng.randn(30, 5)
    X[:10] += 2
    g = mixture.GMM(n_components=2, covariance_type='spherical',
                    random_state=rng, min_covar=1e-7, n_iter=5)
    with ignore_warnings(category=DeprecationWarning):
        train1 = g.fit(X).score(X).sum()
        g.n_init = 5
        train2 = g.fit(X).score(X).sum()
    assert_true(train2 >= train1 - 1.e-2)


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_n_parameters():
    """
    Test the number of parameters for different covariance types.
    
    This function evaluates the number of parameters for a Gaussian Mixture Model (GMM) with varying covariance types: 'full', 'tied', 'diag', and 'spherical'. It generates random data using `numpy.random.randn` and fits the GMM model using `mixture.GMM`. The function asserts that the calculated number of parameters matches the expected values for each covariance type.
    
    Parameters:
    None
    
    Returns:
    None
    """

    n_samples, n_dim, n_components = 7, 5, 2
    X = rng.randn(n_samples, n_dim)
    n_params = {'spherical': 13, 'diag': 21, 'tied': 26, 'full': 41}
    for cv_type in ['full', 'tied', 'diag', 'spherical']:
        with ignore_warnings(category=DeprecationWarning):
            g = mixture.GMM(n_components=n_components, covariance_type=cv_type,
                            random_state=rng, min_covar=1e-7, n_iter=1)
            g.fit(X)
            assert_true(g._n_parameters() == n_params[cv_type])


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_1d_1component():
    """
    Test the BIC scores for Gaussian Mixture Models (GMM) with different covariance types on 1-dimensional data with a single component.
    
    This function evaluates the Bayesian Information Criterion (BIC) scores for GMMs with various covariance types ('full', 'tied', 'diag', 'spherical') when fitting 1-dimensional data with a single component. The BIC scores are compared to ensure they are consistent across different covariance types.
    
    Parameters:
    None
    
    Returns:
    """

    # Test all of the covariance_types return the same BIC score for
    # 1-dimensional, 1 component fits.
    n_samples, n_dim, n_components = 100, 1, 1
    X = rng.randn(n_samples, n_dim)
    g_full = mixture.GMM(n_components=n_components, covariance_type='full',
                         random_state=rng, min_covar=1e-7, n_iter=1)
    with ignore_warnings(category=DeprecationWarning):
        g_full.fit(X)
        g_full_bic = g_full.bic(X)
        for cv_type in ['tied', 'diag', 'spherical']:
            g = mixture.GMM(n_components=n_components, covariance_type=cv_type,
                            random_state=rng, min_covar=1e-7, n_iter=1)
            g.fit(X)
            assert_array_almost_equal(g.bic(X), g_full_bic)


def assert_fit_predict_correct(model, X):
    """
    Assert that the fit and predict methods of a clustering model produce identical results.
    
    This function takes a clustering model and a dataset `X`, fits the model to `X` using both the `fit` and `fit_predict` methods, and then compares the resulting cluster assignments using the Adjusted Rand Score (ARS). The ARS is a measure of similarity between two clusterings, with a perfect score of 1.0 indicating that the two sets of cluster assignments are identical.
    
    Parameters:
    """

    model2 = copy.deepcopy(model)

    predictions_1 = model.fit(X).predict(X)
    predictions_2 = model2.fit_predict(X)

    assert adjusted_rand_score(predictions_1, predictions_2) == 1.0


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_fit_predict():
    """
    test that gmm.fit_predict is equivalent to gmm.fit + gmm.predict
    """
    lrng = np.random.RandomState(101)

    n_samples, n_dim, n_comps = 100, 2, 2
    mu = np.array([[8, 8]])
    component_0 = lrng.randn(n_samples, n_dim)
    component_1 = lrng.randn(n_samples, n_dim) + mu
    X = np.vstack((component_0, component_1))

    for m_constructor in (mixture.GMM, mixture.VBGMM, mixture.DPGMM):
        model = m_constructor(n_components=n_comps, covariance_type='full',
                              min_covar=1e-7, n_iter=5,
                              random_state=np.random.RandomState(0))
        assert_fit_predict_correct(model, X)

    model = mixture.GMM(n_components=n_comps, n_iter=0)
    z = model.fit_predict(X)
    assert np.all(z == 0), "Quick Initialization Failed!"


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_aic():
    """
    Test the AIC and BIC criteria for Gaussian Mixture Models.
    
    This function evaluates the accuracy of the AIC (Akaike Information Criterion)
    and BIC (Bayesian Information Criterion) for different covariance types in
    Gaussian Mixture Models (GMM). It generates random data, fits GMMs with
    varying covariance types, and compares the calculated AIC and BIC values
    against expected theoretical values.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Test the aic and bic criteria
    n_samples, n_dim, n_components = 50, 3, 2
    X = rng.randn(n_samples, n_dim)
    SGH = 0.5 * (X.var() + np.log(2 * np.pi))  # standard gaussian entropy

    for cv_type in ['full', 'tied', 'diag', 'spherical']:
        g = mixture.GMM(n_components=n_components, covariance_type=cv_type,
                        random_state=rng, min_covar=1e-7)
        g.fit(X)
        aic = 2 * n_samples * SGH * n_dim + 2 * g._n_parameters()
        bic = (2 * n_samples * SGH * n_dim +
               np.log(n_samples) * g._n_parameters())
        bound = n_dim * 3. / np.sqrt(n_samples)
        assert_true(np.abs(g.aic(X) - aic) / n_samples < bound)
        assert_true(np.abs(g.bic(X) - bic) / n_samples < bound)


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def check_positive_definite_covars(covariance_type):
    r"""Test that covariance matrices do not become non positive definite

    Due to the accumulation of round-off errors, the computation of the
    covariance  matrices during the learning phase could lead to non-positive
    definite covariance matrices. Namely the use of the formula:

    .. math:: C = (\sum_i w_i  x_i x_i^T) - \mu \mu^T

    instead of:

    .. math:: C = \sum_i w_i (x_i - \mu)(x_i - \mu)^T

    while mathematically equivalent, was observed a ``LinAlgError`` exception,
    when computing a ``GMM`` with full covariance matrices and fixed mean.

    This function ensures that some later optimization will not introduce the
    problem again.
    """
    rng = np.random.RandomState(1)
    # we build a dataset with 2 2d component. The components are unbalanced
    # (respective weights 0.9 and 0.1)
    X = rng.randn(100, 2)
    X[-10:] += (3, 3)  # Shift the 10 last points

    gmm = mixture.GMM(2, params="wc", covariance_type=covariance_type,
                      min_covar=1e-3)

    # This is a non-regression test for issue #2640. The following call used
    # to trigger:
    # numpy.linalg.linalg.LinAlgError: 2-th leading minor not positive definite
    gmm.fit(X)

    if covariance_type == "diag" or covariance_type == "spherical":
        assert_greater(gmm.covars_.min(), 0)
    else:
        if covariance_type == "tied":
            covs = [gmm.covars_]
        else:
            covs = gmm.covars_

        for c in covs:
            assert_greater(np.linalg.det(c), 0)


@pytest.mark.parametrize('covariance_type',
                         ["full", "tied", "diag", "spherical"])
def test_positive_definite_covars(covariance_type):
    # Check positive definiteness for all covariance types
    check_positive_definite_covars(covariance_type)


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_verbose_first_level():
    """
    Fit a Gaussian Mixture Model (GMM) to the given data using verbose output.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Summary:
    This function creates a sample dataset `X` with 30 samples and 5 features. It then adds a constant value of 2 to the first 10 samples to create a clear separation between two clusters. A Gaussian Mixture Model (GMM) is fitted to this data using the `
    """

    # Create sample data
    X = rng.randn(30, 5)
    X[:10] += 2
    g = mixture.GMM(n_components=2, n_init=2, verbose=1)

    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        g.fit(X)
    finally:
        sys.stdout = old_stdout


# This function tests the deprecated old GMM class
@ignore_warnings(category=DeprecationWarning)
def test_verbose_second_level():
    """
    Fit a Gaussian Mixture Model (GMM) to the given data using verbose output.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Summary:
    This function creates a sample dataset `X` with 30 samples and 5 features. It then adds a constant value of 2 to the first 10 samples to introduce a shift. A Gaussian Mixture Model (GMM) is fitted to this data using the `mixture.GMM
    """

    # Create sample data
    X = rng.randn(30, 5)
    X[:10] += 2
    g = mixture.GMM(n_components=2, n_init=2, verbose=2)

    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        g.fit(X)
    finally:
        sys.stdout = old_stdout
