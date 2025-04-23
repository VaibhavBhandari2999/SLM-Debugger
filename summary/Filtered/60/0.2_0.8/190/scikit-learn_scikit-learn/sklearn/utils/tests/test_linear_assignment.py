# Author: Brian M. Clapper, G Varoquaux
# License: BSD

import numpy as np

# XXX we should be testing the public API here
from sklearn.utils.linear_assignment_ import _hungarian


def test_hungarian():
    """
    Tests the hungarian function for correctness.
    
    This function tests the hungarian function with a series of predefined cost matrices and expected total costs. It checks both the original and transposed matrices to ensure the function works correctly for square and rectangular matrices.
    
    Parameters:
    - cost_matrix (list of lists): The cost matrix for the assignment problem.
    - expected_total (int or float): The expected total cost for the given cost matrix.
    
    The function asserts that the calculated total cost matches the expected total cost for both the
    """

    matrices = [
        # Square
        ([[400, 150, 400],
          [400, 450, 600],
          [300, 225, 300]],
         850  # expected cost
         ),

        # Rectangular variant
        ([[400, 150, 400, 1],
          [400, 450, 600, 2],
          [300, 225, 300, 3]],
         452  # expected cost
         ),

        # Square
        ([[10, 10,  8],
          [9,  8,  1],
          [9,  7,  4]],
         18
         ),

        # Rectangular variant
        ([[10, 10,  8, 11],
          [9, 8, 1, 1],
          [9, 7, 4, 10]],
         15
         ),

        # n == 2, m == 0 matrix
        ([[], []],
         0
         ),
    ]

    for cost_matrix, expected_total in matrices:
        cost_matrix = np.array(cost_matrix)
        indexes = _hungarian(cost_matrix)
        total_cost = 0
        for r, c in indexes:
            x = cost_matrix[r, c]
            total_cost += x
        assert expected_total == total_cost

        indexes = _hungarian(cost_matrix.T)
        total_cost = 0
        for c, r in indexes:
            x = cost_matrix[r, c]
            total_cost += x
        assert expected_total == total_cost
