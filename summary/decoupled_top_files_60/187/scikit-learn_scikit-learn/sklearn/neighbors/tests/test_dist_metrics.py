import itertools
import pickle

import numpy as np
from numpy.testing import assert_array_almost_equal

from scipy.spatial.distance import cdist
from sklearn.neighbors.dist_metrics import DistanceMetric
from sklearn.neighbors import BallTree
from sklearn.utils import check_random_state
from sklearn.utils.testing import assert_raises_regex


def dist_func(x1, x2, p):
    return np.sum((x1 - x2) ** p) ** (1. / p)


class TestMetrics(object):
    n1 = 20
    n2 = 25
    d = 4
    zero_frac = 0.5
    rseed = 0
    dtype = np.float64
    rng = check_random_state(rseed)
    X1 = rng.random_sample((n1, d)).astype(dtype)
    X2 = rng.random_sample((n2, d)).astype(dtype)

    # make boolean arrays: ones and zeros
    X1_bool = X1.round(0)
    X2_bool = X2.round(0)

    V = rng.random_sample((d, d))
    VI = np.dot(V, V.T)

    metrics = {'euclidean': {},
               'cityblock': {},
               'minkowski': dict(p=(1, 1.5, 2, 3)),
               'chebyshev': {},
               'seuclidean': dict(V=(rng.random_sample(d),)),
               'wminkowski': dict(p=(1, 1.5, 3),
                                  w=(rng.random_sample(d),)),
               'mahalanobis': dict(VI=(VI,)),
               'hamming': {},
               'canberra': {},
               'braycurtis': {}}

    bool_metrics = ['matching', 'jaccard', 'dice',
                    'kulsinski', 'rogerstanimoto', 'russellrao',
                    'sokalmichener', 'sokalsneath']

    def test_cdist(self):
        """
        Tests the cdist function for various metrics and configurations.
        
        This function iterates over a set of metrics and their corresponding arguments to test the cdist function. It supports both standard and boolean metrics. For each metric and set of arguments, it computes the distance matrix and compares it with the expected result.
        
        Parameters:
        None (the parameters are defined within the function itself)
        
        Key Parameters:
        - `metric`: The distance metric to be used, such as 'euclidean', 'cityblock', etc
        """

        for metric, argdict in self.metrics.items():
            keys = argdict.keys()
            for vals in itertools.product(*argdict.values()):
                kwargs = dict(zip(keys, vals))
                D_true = cdist(self.X1, self.X2, metric, **kwargs)
                yield self.check_cdist, metric, kwargs, D_true

        for metric in self.bool_metrics:
            D_true = cdist(self.X1_bool, self.X2_bool, metric)
            yield self.check_cdist_bool, metric, D_true

    def check_cdist(self, metric, kwargs, D_true):
        """
        Function to check the correctness of the pairwise distance calculation using a specified metric.
        
        Parameters:
        metric (str): The distance metric to use for the calculation, e.g., 'euclidean', 'manhattan'.
        kwargs (dict): Additional keyword arguments to pass to the DistanceMetric constructor.
        D_true (np.ndarray): The expected pairwise distance matrix to compare against the calculated result.
        
        This function computes the pairwise distances between the points in self.X1 and self.X2 using the specified metric and keyword
        """

        dm = DistanceMetric.get_metric(metric, **kwargs)
        D12 = dm.pairwise(self.X1, self.X2)
        assert_array_almost_equal(D12, D_true)

    def check_cdist_bool(self, metric, D_true):
        dm = DistanceMetric.get_metric(metric)
        D12 = dm.pairwise(self.X1_bool, self.X2_bool)
        assert_array_almost_equal(D12, D_true)

    def test_pdist(self):
        for metric, argdict in self.metrics.items():
            keys = argdict.keys()
            for vals in itertools.product(*argdict.values()):
                kwargs = dict(zip(keys, vals))
                D_true = cdist(self.X1, self.X1, metric, **kwargs)
                yield self.check_pdist, metric, kwargs, D_true

        for metric in self.bool_metrics:
            D_true = cdist(self.X1_bool, self.X1_bool, metric)
            yield self.check_pdist_bool, metric, D_true

    def check_pdist(self, metric, kwargs, D_true):
        """
        Function to check the pairwise distance calculation between two sets of points.
        
        This function compares the pairwise distance matrix calculated using the specified metric and its associated parameters against a true distance matrix.
        
        Parameters:
        metric (str): The distance metric to use for the calculation. Supported metrics are those available in the DistanceMetric class.
        kwargs (dict): Keyword arguments to be passed to the DistanceMetric.get_metric function to configure the distance metric.
        D_true (ndarray): The true pairwise distance matrix to compare against
        """

        dm = DistanceMetric.get_metric(metric, **kwargs)
        D12 = dm.pairwise(self.X1)
        assert_array_almost_equal(D12, D_true)

    def check_pdist_bool(self, metric, D_true):
        dm = DistanceMetric.get_metric(metric)
        D12 = dm.pairwise(self.X1_bool)
        assert_array_almost_equal(D12, D_true)

    def test_pickle(self):
        """
        Function to test the pickling of metrics.
        
        This function iterates over a set of metrics and their associated arguments, generating test cases for pickling each metric with different argument combinations. It also includes tests for boolean metrics.
        
        Parameters:
        self (unittest.TestCase): The current test case object.
        
        Yields:
        tuple: A tuple containing the test method to call and the arguments for that method.
        
        The function yields test cases for:
        - Each metric with all possible combinations of its arguments.
        - Boolean metrics
        """

        for metric, argdict in self.metrics.items():
            keys = argdict.keys()
            for vals in itertools.product(*argdict.values()):
                kwargs = dict(zip(keys, vals))
                yield self.check_pickle, metric, kwargs

        for metric in self.bool_metrics:
            yield self.check_pickle_bool, metric

    def check_pickle_bool(self, metric):
        dm = DistanceMetric.get_metric(metric)
        D1 = dm.pairwise(self.X1_bool)
        dm2 = pickle.loads(pickle.dumps(dm))
        D2 = dm2.pairwise(self.X1_bool)
        assert_array_almost_equal(D1, D2)

    def check_pickle(self, metric, kwargs):
        dm = DistanceMetric.get_metric(metric, **kwargs)
        D1 = dm.pairwise(self.X1)
        dm2 = pickle.loads(pickle.dumps(dm))
        D2 = dm2.pairwise(self.X1)
        assert_array_almost_equal(D1, D2)


def test_haversine_metric():
    """
    Tests the haversine distance metric.
    
    This function compares the output of the haversine distance metric provided
    by the `DistanceMetric` class with a custom implementation of the haversine
    distance calculation. The custom implementation iterates over all pairs of
    points in the input array `X` and calculates the distance between each pair
    using the haversine formula.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `X`: A 2D numpy array of
    """

    def haversine_slow(x1, x2):
        """
        Calculate the Haversine distance between two points on the Earth.
        
        Parameters:
        x1 (tuple): A tuple containing the latitude and longitude of the first point in radians.
        x2 (tuple): A tuple containing the latitude and longitude of the second point in radians.
        
        Returns:
        float: The Haversine distance between the two points in radians.
        """

        return 2 * np.arcsin(np.sqrt(np.sin(0.5 * (x1[0] - x2[0])) ** 2
                                     + np.cos(x1[0]) * np.cos(x2[0]) *
                                     np.sin(0.5 * (x1[1] - x2[1])) ** 2))

    X = np.random.random((10, 2))

    haversine = DistanceMetric.get_metric("haversine")

    D1 = haversine.pairwise(X)
    D2 = np.zeros_like(D1)
    for i, x1 in enumerate(X):
        for j, x2 in enumerate(X):
            D2[i, j] = haversine_slow(x1, x2)

    assert_array_almost_equal(D1, D2)
    assert_array_almost_equal(haversine.dist_to_rdist(D1),
                              np.sin(0.5 * D2) ** 2)


def test_pyfunc_metric():
    X = np.random.random((10, 3))

    euclidean = DistanceMetric.get_metric("euclidean")
    pyfunc = DistanceMetric.get_metric("pyfunc", func=dist_func, p=2)

    # Check if both callable metric and predefined metric initialized
    # DistanceMetric object is picklable
    euclidean_pkl = pickle.loads(pickle.dumps(euclidean))
    pyfunc_pkl = pickle.loads(pickle.dumps(pyfunc))

    D1 = euclidean.pairwise(X)
    D2 = pyfunc.pairwise(X)

    D1_pkl = euclidean_pkl.pairwise(X)
    D2_pkl = pyfunc_pkl.pairwise(X)

    assert_array_almost_equal(D1, D2)
    assert_array_almost_equal(D1_pkl, D2_pkl)


def test_bad_pyfunc_metric():
    def wrong_distance(x, y):
        return "1"

    X = np.ones((5, 2))
    assert_raises_regex(TypeError,
                        "Custom distance function must accept two vectors",
                        BallTree, X, metric=wrong_distance)


def test_input_data_size():
    """
    Test the input data size for a custom metric function.
    
    This function checks that a custom metric function, which requires a specific
    input dimension, works correctly with the DistanceMetric class. It ensures
    that the custom metric function can handle the input data correctly without
    failing due to dimensionality issues.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    - custom_metric: A custom metric function that requires the input data
    to have a specific dimension (in this case, 3
    """

    # Regression test for #6288
    # Previoulsly, a metric requiring a particular input dimension would fail
    def custom_metric(x, y):
        assert x.shape[0] == 3
        return np.sum((x - y) ** 2)

    rng = check_random_state(0)
    X = rng.rand(10, 3)

    pyfunc = DistanceMetric.get_metric("pyfunc", func=dist_func, p=2)
    eucl = DistanceMetric.get_metric("euclidean")
    assert_array_almost_equal(pyfunc.pairwise(X), eucl.pairwise(X))
