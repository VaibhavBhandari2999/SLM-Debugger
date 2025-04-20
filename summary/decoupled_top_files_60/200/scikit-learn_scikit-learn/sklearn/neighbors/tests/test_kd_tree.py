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
    Check that the KDTree neighbors are the same as brute force neighbors.
    
    Parameters
    ----------
    dualtree : bool
    Whether to use the dual tree search.
    breadth_first : bool
    Whether to use the breadth-first search.
    k : int
    Number of neighbors to find.
    metric : str
    The distance metric to use.
    X : array-like
    The input data points for the KDTree.
    Y : array-like
    The query points for which to find neighbors.
    kwargs
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
    """
    Tests the KDTree query functionality for a given metric.
    
    This function evaluates the KDTree query method for a specified metric, number of nearest neighbors (k), and whether to use a dualtree or single tree approach. It also checks the breadth-first search option.
    
    Parameters:
    metric (str): The distance metric to use for the query, e.g., 'euclidean', 'manhattan'.
    k (int): The number of nearest neighbors to find.
    dualtree (bool): Whether to
    """

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
    """
    Compare the results of the Gaussian KDE (Kernel Density Estimation) using the `KDTree` method to the `gaussian_kde` function from `scipy.stats`.
    
    Parameters:
    n_samples (int): The number of sample points to generate for the KDE. Default is 1000.
    
    Returns:
    None: This function does not return any value. It asserts that the KDE results from the `KDTree` method are almost equal to the results from `gaussian_kde
    """

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
    """
    Compute the two-point correlation function for a set of points.
    
    This function calculates the two-point correlation function for a set of
    points `Y` with respect to another set of points `X` using a KDTree. The
    correlation function is computed for a range of distances `r`.
    
    Parameters:
    X : array-like, shape (n_samples, n_features)
    The input dataset representing the first set of points.
    Y : array-like, shape (m_samples, n_features)
    """

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
    """
    Test the NeighborsHeap functionality.
    
    This function initializes a NeighborsHeap with a specified number of points and neighbors. It then pushes a series of distances and indices into the heap and retrieves the nearest neighbors. The function verifies that the retrieved distances and indices match the expected sorted order.
    
    Parameters:
    n_pts (int): The number of points in the heap.
    n_nbrs (int): The number of nearest neighbors to keep for each point.
    
    Returns:
    None: This function does not return
    """

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
