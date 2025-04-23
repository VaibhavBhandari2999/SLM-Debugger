import pickle
import numpy as np
from sklearn.neighbors.quad_tree import _QuadTree
from sklearn.utils import check_random_state


def test_quadtree_boundary_computation():
    """
    Function to test the boundary computation in a quad tree.
    
    This function tests the boundary computation in a quad tree by inserting points with various configurations and checking the coherence of the tree structure.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function tests the quad tree with different point configurations.
    - Configurations include random points, points with only zeros, points with only negative values, and points with very small values.
    - The function builds the quad tree and checks its coherence
    """

    # Introduce a point into a quad tree with boundaries not easy to compute.
    Xs = []

    # check a random case
    Xs.append(np.array([[-1, 1], [-4, -1]], dtype=np.float32))
    # check the case where only 0 are inserted
    Xs.append(np.array([[0, 0], [0, 0]], dtype=np.float32))
    # check the case where only negative are inserted
    Xs.append(np.array([[-1, -2], [-4, 0]], dtype=np.float32))
    # check the case where only small numbers are inserted
    Xs.append(np.array([[-1e-6, 1e-6], [-4e-6, -1e-6]], dtype=np.float32))

    for X in Xs:
        tree = _QuadTree(n_dimensions=2, verbose=0)
        tree.build_tree(X)
        tree._check_coherence()


def test_quadtree_similar_point():
    # Introduce a point into a quad tree where a similar point already exists.
    # Test will hang if it doesn't complete.
    Xs = []

    # check the case where points are actually different
    Xs.append(np.array([[1, 2], [3, 4]], dtype=np.float32))
    # check the case where points are the same on X axis
    Xs.append(np.array([[1.0, 2.0], [1.0, 3.0]], dtype=np.float32))
    # check the case where points are arbitrarily close on X axis
    Xs.append(np.array([[1.00001, 2.0], [1.00002, 3.0]], dtype=np.float32))
    # check the case where points are the same on Y axis
    Xs.append(np.array([[1.0, 2.0], [3.0, 2.0]], dtype=np.float32))
    # check the case where points are arbitrarily close on Y axis
    Xs.append(np.array([[1.0, 2.00001], [3.0, 2.00002]], dtype=np.float32))
    # check the case where points are arbitrarily close on both axes
    Xs.append(np.array([[1.00001, 2.00001], [1.00002, 2.00002]],
              dtype=np.float32))

    # check the case where points are arbitrarily close on both axes
    # close to machine epsilon - x axis
    Xs.append(np.array([[1, 0.0003817754041], [2, 0.0003817753750]],
              dtype=np.float32))

    # check the case where points are arbitrarily close on both axes
    # close to machine epsilon - y axis
    Xs.append(np.array([[0.0003817754041, 1.0], [0.0003817753750, 2.0]],
              dtype=np.float32))

    for X in Xs:
        tree = _QuadTree(n_dimensions=2, verbose=0)
        tree.build_tree(X)
        tree._check_coherence()


def test_quad_tree_pickle():
    rng = check_random_state(0)

    for n_dimensions in (2, 3):
        X = rng.random_sample((10, n_dimensions))

        tree = _QuadTree(n_dimensions=n_dimensions, verbose=0)
        tree.build_tree(X)

        def check_pickle_protocol(protocol):
            s = pickle.dumps(tree, protocol=protocol)
            bt2 = pickle.loads(s)

            for x in X:
                cell_x_tree = tree.get_cell(x)
                cell_x_bt2 = bt2.get_cell(x)
                assert cell_x_tree == cell_x_bt2

        for protocol in (0, 1, 2):
            yield check_pickle_protocol, protocol


def test_qt_insert_duplicate():
    """
    Test function to check the behavior of a quadtree when inserting duplicate points.
    
    This function verifies that when duplicate points are inserted into a quadtree,
    the quadtree correctly handles and counts these duplicates. The function tests
    this behavior for both 2-dimensional and 3-dimensional data.
    
    Parameters:
    n_dimensions (int): The number of dimensions of the input data. Can be either 2 or 3.
    
    Returns:
    None: This function does not return any value. It asserts conditions to ensure
    """

    rng = check_random_state(0)

    def check_insert_duplicate(n_dimensions=2):
        """
        Checks for duplicate insertion in a quadtree.
        
        This function tests the behavior of a quadtree when inserting duplicate points.
        It builds a quadtree with a given number of dimensions and inserts a set of points,
        including some duplicates. The function then verifies that the quadtree correctly
        identifies and handles the duplicates.
        
        Parameters:
        n_dimensions (int, optional): The number of dimensions for the quadtree. Default is 2.
        
        Returns:
        None: The function does not return any value. It
        """


        X = rng.random_sample((10, n_dimensions))
        Xd = np.r_[X, X[:5]]
        tree = _QuadTree(n_dimensions=n_dimensions, verbose=0)
        tree.build_tree(Xd)

        cumulative_size = tree.cumulative_size
        leafs = tree.leafs

        # Assert that the first 5 are indeed duplicated and that the next
        # ones are single point leaf
        for i, x in enumerate(X):
            cell_id = tree.get_cell(x)
            assert leafs[cell_id]
            assert cumulative_size[cell_id] == 1 + (i < 5)

    for n_dimensions in (2, 3):
        yield check_insert_duplicate, n_dimensions


def test_summarize():
    _QuadTree.test_summarize()
