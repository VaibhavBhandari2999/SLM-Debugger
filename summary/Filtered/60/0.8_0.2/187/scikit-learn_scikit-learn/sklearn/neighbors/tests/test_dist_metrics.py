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
        dm = DistanceMetric.get_metric(metric, **kwargs)
        D12 = dm.pairwise(self.X1)
        assert_array_almost_equal(D12, D_true)

    def check_pdist_bool(self, metric, D_true):
        dm = DistanceMetric.get_metric(metric)
        D12 = dm.pairwise(self.X1_bool)
        assert_array_almost_equal(D12, D_true)

    def test_pickle(self):
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
        """
        Function to check the consistency of a distance metric implementation using pickling.
        
        Parameters:
        metric (str): The name of the distance metric to be used.
        kwargs (dict): Additional keyword arguments required by the distance metric.
        
        This function creates a distance metric object, computes the pairwise distances on a dataset (self.X1), pickles and unpickles the object, recomputes the pairwise distances, and asserts that the original and new distance matrices are almost equal.
        
        Returns:
        None: The
        """

        dm = DistanceMetric.get_metric(metric, **kwargs)
        D1 = dm.pairwise(self.X1)
        dm2 = pickle.loads(pickle.dumps(dm))
        D2 = dm2.pairwise(self.X1)
        assert_array_almost_equal(D1, D2)


def test_haversine_metric():
    def haversine_slow(x1, x2):
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
    """
    Test a custom distance function that does not accept the correct number of arguments.
    
    This function checks if a custom distance function that does not accept two vectors
    raises a TypeError when used with the BallTree class. The custom function `wrong_distance`
    returns a string instead of a numeric distance value.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If the custom distance function is not properly defined to accept
    two vectors as arguments.
    """

    def wrong_distance(x, y):
        return "1"

    X = np.ones((5, 2))
    assert_raises_regex(TypeError,
                        "Custom distance function must accept two vectors",
                        BallTree, X, metric=wrong_distance)


def test_input_data_size():
    """
    Test input data size for custom metric function.
    
    This function tests a custom metric function to ensure it correctly handles
    input data with a specific dimension. The custom metric function is used to
    calculate the pairwise distances between rows in a dataset.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The custom metric function `custom_metric` is defined within the function
    and checks if the input data has 3 columns.
    - The function uses `check_random_state` to generate a
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
