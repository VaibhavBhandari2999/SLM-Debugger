import numpy as np
from numpy.testing import assert_array_almost_equal

import pytest

from sklearn.neighbors.kd_tree import (KDTree, NeighborsHeap,
                                       simultaneous_sort, kernel_norm,
                                       nodeheap_sort, DTYPE, ITYPE)
from sklearn.neighbors.dist_metrics import DistanceMetric
from sklearn.utils import check_random_state
from sklearn.utils.testing import assert_allclose

rng = np.random.RandomState(42)
V = rng.random_sample((3, 3))
V = np.dot(V, V.T)

DIMENSION = 3

METRICS = {'euclidean': {},
           'manhattan': {},
           'chebyshev': {},
           'minkowski': dict(p=3)}


def brute_force_neighbors(X, Y, k, metric, **kwargs):
    D = DistanceMetric.get_metric(metric, **kwargs).pairwise(Y, X)
    ind = np.argsort(D, axis=1)[:, :k]
    dist = D[np.arange(Y.shape[0])[:, None], ind]
    return dist, ind


def check_neighbors(dualtree, breadth_first, k, metric, X, Y, kwargs):
    """
    Check the neighbors of points in a dataset using a KDTree and a brute force method.
    
    This function compares the nearest neighbors found by a KDTree with those found
    by a brute force method. It ensures that the distances to the nearest neighbors
    are the same for both methods.
    
    Parameters:
    dualtree (bool): Whether to use dualtree algorithm for KDTree queries.
    breadth_first (bool): Whether to use breadth-first search for KDTree queries.
    k (int): The number of
    """

    kdt = KDTree(X, leaf_size=1, metric=metric, **kwargs)
    dist1, ind1 = kdt.query(Y, k, dualtree=dualtree,
                            breadth_first=breadth_first)
    dist2, ind2 = brute_force_neighbors(X, Y, k, metric, **kwargs)

    # don't check indices here: if there are any duplicate distances,
    # the indices may not match.  Distances should not have this problem.
    assert_array_almost_equal(dist1, dist2)


@pytest.mark.parametrize('metric', METRICS)
@pytest.mark.parametrize('k', (1, 3, 5))
@pytest.mark.parametrize('dualtree', (True, False))
@pytest.mark.parametrize('breadth_first', (True, False))
def test_kd_tree_query(metric, k, dualtree, breadth_first):
    rng = check_random_state(0)
    X = rng.random_sample((40, DIMENSION))
    Y = rng.random_sample((10, DIMENSION))

    kwargs = METRICS[metric]
    check_neighbors(dualtree, breadth_first, k, metric, X, Y, kwargs)


def test_kd_tree_query_radius(n_samples=100, n_features=10):
    rng = check_random_state(0)
    X = 2 * rng.random_sample(size=(n_samples, n_features)) - 1
    query_pt = np.zeros(n_features, dtype=float)

    eps = 1E-15  # roundoff error can cause test to fail
    kdt = KDTree(X, leaf_size=5)
    rad = np.sqrt(((X - query_pt) ** 2).sum(1))

    for r in np.linspace(rad[0], rad[-1], 100):
        ind = kdt.query_radius([query_pt], r + eps)[0]
        i = np.where(rad <= r + eps)[0]

        ind.sort()
        i.sort()

        assert_array_almost_equal(i, ind)


def test_kd_tree_query_radius_distance(n_samples=100, n_features=10):
    rng = check_random_state(0)
    X = 2 * rng.random_sample(size=(n_samples, n_features)) - 1
    query_pt = np.zeros(n_features, dtype=float)

    eps = 1E-15  # roundoff error can cause test to fail
    kdt = KDTree(X, leaf_size=5)
    rad = np.sqrt(((X - query_pt) ** 2).sum(1))

    for r in np.linspace(rad[0], rad[-1], 100):
        ind, dist = kdt.query_radius([query_pt], r + eps, return_distance=True)

        ind = ind[0]
        dist = dist[0]

        d = np.sqrt(((query_pt - X[ind]) ** 2).sum(1))

        assert_array_almost_equal(d, dist)


def compute_kernel_slow(Y, X, kernel, h):
    d = np.sqrt(((Y[:, None, :] - X) ** 2).sum(-1))
    norm = kernel_norm(h, X.shape[1], kernel)

    if kernel == 'gaussian':
        return norm * np.exp(-0.5 * (d * d) / (h * h)).sum(-1)
    elif kernel == 'tophat':
        return norm * (d < h).sum(-1)
    elif kernel == 'epanechnikov':
        return norm * ((1.0 - (d * d) / (h * h)) * (d < h)).sum(-1)
    elif kernel == 'exponential':
        return norm * (np.exp(-d / h)).sum(-1)
    elif kernel == 'linear':
        return norm * ((1 - d / h) * (d < h)).sum(-1)
    elif kernel == 'cosine':
        return norm * (np.cos(0.5 * np.pi * d / h) * (d < h)).sum(-1)
    else:
        raise ValueError('kernel not recognized')


def check_results(kernel, h, atol, rtol, breadth_first, Y, kdt, dens_true):
    dens = kdt.kernel_density(Y, h, atol=atol, rtol=rtol,
                              kernel=kernel,
                              breadth_first=breadth_first)
    assert_allclose(dens, dens_true, atol=atol,
                    rtol=max(rtol, 1e-7))


@pytest.mark.parametrize('kernel',
                         ['gaussian', 'tophat', 'epanechnikov',
                          'exponential', 'linear', 'cosine'])
@pytest.mark.parametrize('h', [0.01, 0.1, 1])
def test_kd_tree_kde(kernel, h):
    """
    Tests the Kernel Density Estimation (KDE) using a KDTree for a given kernel and bandwidth.
    
    This function evaluates the accuracy of the KDE computation using a KDTree by comparing the results of a fast KDE implementation with a slow, brute-force method.
    
    Parameters
    ----------
    kernel : str
    The kernel function to use for density estimation. Supported kernels include 'gaussian', 'tophat', 'epanechnikov', 'exponential', 'linear', and 'cosine'.
    h :
    """

    n_samples, n_features = (100, 3)
    rng = check_random_state(0)
    X = rng.random_sample((n_samples, n_features))
    Y = rng.random_sample((n_samples, n_features))
    kdt = KDTree(X, leaf_size=10)

    dens_true = compute_kernel_slow(Y, X, kernel, h)

    for rtol in [0, 1E-5]:
        for atol in [1E-6, 1E-2]:
            for breadth_first in (True, False):
                check_results(kernel, h, atol, rtol,
                              breadth_first, Y, kdt, dens_true)


def test_gaussian_kde(n_samples=1000):
    # Compare gaussian KDE results to scipy.stats.gaussian_kde
    from scipy.stats import gaussian_kde
    rng = check_random_state(0)
    x_in = rng.normal(0, 1, n_samples)
    x_out = np.linspace(-5, 5, 30)

    for h in [0.01, 0.1, 1]:
        kdt = KDTree(x_in[:, None])
        gkde = gaussian_kde(x_in, bw_method=h / np.std(x_in))

        dens_kdt = kdt.kernel_density(x_out[:, None], h) / n_samples
        dens_gkde = gkde.evaluate(x_out)

        assert_array_almost_equal(dens_kdt, dens_gkde, decimal=3)


@pytest.mark.parametrize('dualtree', (True, False))
def test_kd_tree_two_point(dualtree):
    n_samples, n_features = (100, 3)
    rng = check_random_state(0)
    X = rng.random_sample((n_samples, n_features))
    Y = rng.random_sample((n_samples, n_features))
    r = np.linspace(0, 1, 10)
    kdt = KDTree(X, leaf_size=10)

    D = DistanceMetric.get_metric("euclidean").pairwise(Y, X)
    counts_true = [(D <= ri).sum() for ri in r]

    counts = kdt.two_point_correlation(Y, r=r, dualtree=dualtree)
    assert_array_almost_equal(counts, counts_true)


@pytest.mark.parametrize('protocol', (0, 1, 2))
def test_kd_tree_pickle(protocol):
    """
    Test the pickling of a KDTree object.
    
    Parameters
    ----------
    protocol : int
    The pickle protocol version to use.
    
    This function tests the pickling and unpickling of a KDTree object. It creates
    a KDTree from a random set of points and then pickles and unpickles the object
    using the specified protocol. After unpickling, it queries the KDTree with
    the same points to ensure that the pickled and unpickled objects produce the
    same results
    """

    import pickle
    rng = check_random_state(0)
    X = rng.random_sample((10, 3))
    kdt1 = KDTree(X, leaf_size=1)
    ind1, dist1 = kdt1.query(X)

    def check_pickle_protocol(protocol):
        s = pickle.dumps(kdt1, protocol=protocol)
        kdt2 = pickle.loads(s)
        ind2, dist2 = kdt2.query(X)
        assert_array_almost_equal(ind1, ind2)
        assert_array_almost_equal(dist1, dist2)
        assert isinstance(kdt2, KDTree)

    check_pickle_protocol(protocol)


def test_neighbors_heap(n_pts=5, n_nbrs=10):
    heap = NeighborsHeap(n_pts, n_nbrs)

    for row in range(n_pts):
        d_in = rng.random_sample(2 * n_nbrs).astype(DTYPE, copy=False)
        i_in = np.arange(2 * n_nbrs, dtype=ITYPE)
        for d, i in zip(d_in, i_in):
            heap.push(row, d, i)

        ind = np.argsort(d_in)
        d_in = d_in[ind]
        i_in = i_in[ind]

        d_heap, i_heap = heap.get_arrays(sort=True)

        assert_array_almost_equal(d_in[:n_nbrs], d_heap[row])
        assert_array_almost_equal(i_in[:n_nbrs], i_heap[row])


def test_node_heap(n_nodes=50):
    vals = rng.random_sample(n_nodes).astype(DTYPE, copy=False)

    i1 = np.argsort(vals)
    vals2, i2 = nodeheap_sort(vals)

    assert_array_almost_equal(i1, i2)
    assert_array_almost_equal(vals[i1], vals2)


def test_simultaneous_sort(n_rows=10, n_pts=201):
    dist = rng.random_sample((n_rows, n_pts)).astype(DTYPE, copy=False)
    ind = (np.arange(n_pts) + np.zeros((n_rows, 1))).astype(ITYPE, copy=False)

    dist2 = dist.copy()
    ind2 = ind.copy()

    # simultaneous sort rows using function
    simultaneous_sort(dist, ind)

    # simultaneous sort rows using numpy
    i = np.argsort(dist2, axis=1)
    row_ind = np.arange(n_rows)[:, None]
    dist2 = dist2[row_ind, i]
    ind2 = ind2[row_ind, i]

    assert_array_almost_equal(dist, dist2)
    assert_array_almost_equal(ind, ind2)
