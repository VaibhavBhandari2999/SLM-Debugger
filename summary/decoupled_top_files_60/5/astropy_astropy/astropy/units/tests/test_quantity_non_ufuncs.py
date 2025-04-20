import numpy as np

import pytest

from ... import units as u


class TestQuantityLinAlgFuncs:
    """
    Test linear algebra functions
    """

    @pytest.mark.xfail
    def test_outer(self):
        q1 = np.array([1, 2, 3]) * u.m
        q2 = np.array([1, 2]) / u.s
        o = np.outer(q1, q2)
        assert np.all(o == np.array([[1, 2], [2, 4], [3, 6]]) * u.m / u.s)

    @pytest.mark.xfail
    def test_inner(self):
        """
        Tests the inner product of two numpy arrays with units.
        
        Parameters:
        None
        
        Returns:
        None
        
        This function tests the inner product of two numpy arrays, each containing values with units of meters and seconds. The expected result is a quantity with units of meters per second.
        """

        q1 = np.array([1, 2, 3]) * u.m
        q2 = np.array([4, 5, 6]) / u.s
        o = np.inner(q1, q2)
        assert o == 32 * u.m / u.s

    @pytest.mark.xfail
    def test_dot(self):
        q1 = np.array([1., 2., 3.]) * u.m
        q2 = np.array([4., 5., 6.]) / u.s
        o = np.dot(q1, q2)
        assert o == 32. * u.m / u.s

    @pytest.mark.xfail
    def test_matmul(self):
        """
        Tests matrix multiplication of a quantity matrix with a quantity array.
        
        Parameters:
        q1 (numpy.ndarray): A 3x3 identity matrix with units of meters (m).
        q2 (numpy.ndarray): A 3-element array with units of seconds (s).
        
        Returns:
        numpy.ndarray: The result of the matrix multiplication, with units of meters per second (m/s).
        """

        q1 = np.eye(3) * u.m
        q2 = np.array([4., 5., 6.]) / u.s
        o = np.matmul(q1, q2)
        assert o == q2 / u.s
