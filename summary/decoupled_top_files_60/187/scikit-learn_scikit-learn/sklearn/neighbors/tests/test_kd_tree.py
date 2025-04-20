import numpy as np
from numpy.testing import assert_array_almost_equal
from sklearn.neighbors.kd_tree import (KDTree, NeighborsHeap,
                                       simultaneous_sort, kernel_norm,
                                       nodeheap_sort, DTYPE, ITYPE)
from sklearn.neighbors.dist_metrics import DistanceMetric
from sklearn.utils import check_random_state
from sklearn.utils.testing import SkipTest, assert_allclose

rng = np.random.RandomState(42)
V = rng.random_sample((3, 3))
V = np.dot(V, V.T)

DIMENSION = 3

METRICS = {'euclidean': {},
           'manhattan': {},
           'chebyshev': {},
           'minkowski': dict(p=3)}


def brute_force_neighbors(X, Y, k, metric, **kwargs):
    """
    Generate the k-nearest neighbors for each point in a dataset.
    
    This function computes the k-nearest neighbors for each point in the dataset `Y` with respect to the dataset `X` using a specified distance metric.
    
    Parameters:
    X (array-like, shape (n_samples_X, n_features)): The training dataset.
    Y (array-like, shape (n_samples_Y, n_features)): The dataset for which to find the k-nearest neighbors.
    k (int): The number of
    """

    D = DistanceMetric.get_metric(metric, **kwargs).pairwise(Y, X)
    ind = np.argsort(D, axis=1)[:, :k]
    dist = D[np.arange(Y.shape[0])[:, None], ind]
    return dist, ind


def check_neighbors(dualtree, breadth_first, k, metric, X, Y, kwargs):
    kdt = KDTree(X, leaf_size=1, metric=metric, **kwargs)
    dist1, ind1 = kdt.query(Y, k, dualtree=dualtree,
                            breadth_first=breadth_first)
    dist2, ind2 = brute_force_neighbors(X, Y, k, metric, **kwargs)

    # don't check indices here: if there are any duplicate distances,
    # the indices may not match.  Distances should not have this problem.
    assert_array_almost_equal(dist1, dist2)


def test_kd_tree_query():
    """
    Tests the KDTree query functionality for different configurations.
    
    This function tests the KDTree query method with various parameters to ensure
    correctness. It generates random data points and queries the KDTree with
    different settings for dualtree, breadth_first, k, metric, and kwargs.
    
    Parameters:
    rng (RandomState): A random number generator to generate test data.
    X (ndarray): Input data points for the query tree.
    Y (ndarray): Input data points for the query points.
    """

    rng = check_random_state(0)
    X = rng.random_sample((40, DIMENSION))
    Y = rng.random_sample((10, DIMENSION))

    for (metric, kwargs) in METRICS.items():
        for k in (1, 3, 5):
            for dualtree in (True, False):
                for breadth_first in (True, False):
                    yield (check_neighbors,
                           dualtree, breadth_first,
                           k, metric, X, Y, kwargs)


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
    """
    Check the results of a kernel density estimation.
    
    This function evaluates the accuracy of the kernel density estimation
    performed by the `kdt.kernel_density` method. It compares the estimated
    density with a reference density (`dens_true`) and asserts that the
    estimated density is close to the reference density within specified
    tolerances.
    
    Parameters:
    kernel (str): The kernel function used for density estimation.
    h (float): Bandwidth for the kernel density estimation.
    atol (float): Absolute
    """

    dens = kdt.kernel_density(Y, h, atol=atol, rtol=rtol,
                              kernel=kernel,
                              breadth_first=breadth_first)
    assert_allclose(dens, dens_true, atol=atol,
                    rtol=max(rtol, 1e-7))


def test_kd_tree_kde(n_samples=100, n_features=3):
    rng = check_random_state(0)
    X = rng.random_sample((n_samples, n_features))
    Y = rng.random_sample((n_samples, n_features))
    kdt = KDTree(X, leaf_size=10)

    for kernel in ['gaussian', 'tophat', 'epanechnikov',
                   'exponential', 'linear', 'cosine']:
        for h in [0.01, 0.1, 1]:
            dens_true = compute_kernel_slow(Y, X, kernel, h)

            for rtol in [0, 1E-5]:
                for atol in [1E-6, 1E-2]:
                    for breadth_first in (True, False):
                        yield (check_results, kernel, h, atol, rtol,
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


def test_kd_tree_two_point(n_samples=100, n_features=3):
    """
    Generate a two-point correlation function using a KDTree.
    
    This function calculates the two-point correlation between two sets of points
    using a KDTree data structure. The correlation is computed for a range of
    distances `r`.
    
    Parameters
    ----------
    n_samples : int, optional
    The number of sample points to generate for both X and Y. Default is 100.
    n_features : int, optional
    The number of features for each sample point. Default is 3.
    
    Returns
    """

    rng = check_random_state(0)
    X = rng.random_sample((n_samples, n_features))
    Y = rng.random_sample((n_samples, n_features))
    r = np.linspace(0, 1, 10)
    kdt = KDTree(X, leaf_size=10)

    D = DistanceMetric.get_metric("euclidean").pairwise(Y, X)
    counts_true = [(D <= ri).sum() for ri in r]

    def check_two_point(r, dualtree):
        counts = kdt.two_point_correlation(Y, r=r, dualtree=dualtree)
        assert_array_almost_equal(counts, counts_true)

    for dualtree in (True, False):
        yield check_two_point, r, dualtree


def test_kd_tree_pickle():
    import pickle
    rng = check_random_state(0)
    X = rng.random_sample((10, 3))
    kdt1 = KDTree(X, leaf_size=1)
    ind1, dist1 = kdt1.query(X)

    def check_pickle_protocol(protocol):
        """
        Function to check if a KDTree can be pickled and unpickled using a specific protocol.
        
        Parameters:
        protocol (int): The protocol version for pickling. This should be an integer representing the protocol version to use for pickling.
        
        Returns:
        None: This function does not return any value. It asserts that the KDTree can be pickled and unpickled without losing the query results.
        
        This function serializes a KDTree object using the specified protocol, deserializes it,
        """

        s = pickle.dumps(kdt1, protocol=protocol)
        kdt2 = pickle.loads(s)
        ind2, dist2 = kdt2.query(X)
        assert_array_almost_equal(ind1, ind2)
        assert_array_almost_equal(dist1, dist2)

    for protocol in (0, 1, 2):
        yield check_pickle_protocol, protocol


def test_neighbors_heap(n_pts=5, n_nbrs=10):
    """
    Test the NeighborsHeap functionality.
    
    Parameters:
    n_pts (int): Number of points in the heap.
    n_nbrs (int): Number of nearest neighbors to store for each point.
    
    This function initializes a NeighborsHeap with the specified number of points and nearest neighbors. It then iterates over each point, pushing a set of distances and indices into the heap. After pushing, it retrieves the distances and indices from the heap and compares them to the expected sorted values to ensure the heap is
    """

    heap = NeighborsHeap(n_pts, n_nbrs)

    for row in range(n_pts):
        d_in = rng.random_sample(2 * n_nbrs).astype(DTYPE)
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
    vals = rng.random_sample(n_nodes).astype(DTYPE)

    i1 = np.argsort(vals)
    vals2, i2 = nodeheap_sort(vals)

    assert_array_almost_equal(i1, i2)
    assert_array_almost_equal(vals[i1], vals2)


def test_simultaneous_sort(n_rows=10, n_pts=201):
    dist = rng.random_sample((n_rows, n_pts)).astype(DTYPE)
    ind = (np.arange(n_pts) + np.zeros((n_rows, 1))).astype(ITYPE)

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
