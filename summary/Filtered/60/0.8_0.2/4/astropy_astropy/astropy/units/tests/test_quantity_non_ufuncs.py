import numpy as np

import pytest

from ... import units as u


class TestQuantityLinAlgFuncs:
    """
    Test linear algebra functions
    """

    @pytest.mark.xfail
    def test_outer(self):
        """
        Test the outer product of two Quantity arrays.
        
        Parameters:
        None
        
        Returns:
        None
        
        This function tests the outer product of two Quantity arrays, `q1` and `q2`. `q1` is a 1D array of length 3 with units of meters (m), and `q2` is a 1D array of length 2 with units of seconds (s). The outer product of `q1` and `q2` is computed and the result
        """

        q1 = np.array([1, 2, 3]) * u.m
        q2 = np.array([1, 2]) / u.s
        o = np.outer(q1, q2)
        assert np.all(o == np.array([[1, 2], [2, 4], [3, 6]]) * u.m / u.s)

    @pytest.mark.xfail
    def test_inner(self):
        q1 = np.array([1, 2, 3]) * u.m
        q2 = np.array([4, 5, 6]) / u.s
        o = np.inner(q1, q2)
        assert o == 32 * u.m / u.s

    @pytest.mark.xfail
    def test_dot(self):
        """
        Tests the dot product of two quantities.
        
        Parameters:
        None
        
        Returns:
        None
        
        This function tests the dot product of two quantities, `q1` and `q2`. `q1` is an array of dimensions [1, 2, 3] with units of meters (m), and `q2` is an array of dimensions [4, 5, 6] with units of seconds (s). The function calculates the dot product of `q1` and
        """

        q1 = np.array([1., 2., 3.]) * u.m
        q2 = np.array([4., 5., 6.]) / u.s
        o = np.dot(q1, q2)
        assert o == 32. * u.m / u.s

    @pytest.mark.xfail
    def test_matmul(self):
        q1 = np.eye(3) * u.m
        q2 = np.array([4., 5., 6.]) / u.s
        o = np.matmul(q1, q2)
        assert o == q2 / u.s
