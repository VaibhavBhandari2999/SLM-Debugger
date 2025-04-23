# Author: Guillaume Lemaitre <g.lemaitre58@gmail.com>
# License: BSD 3 clause

import pytest
import numpy as np

from sklearn.mixture import GaussianMixture
from sklearn.mixture import BayesianGaussianMixture


@pytest.mark.parametrize(
    "estimator",
    [GaussianMixture(),
     BayesianGaussianMixture()]
)
def test_gaussian_mixture_n_iter(estimator):
    """
    Test that the number of iterations (`n_iter_`) matches the maximum number of iterations (`max_iter`) set for the Gaussian Mixture Model estimator.
    
    Parameters:
    estimator (GaussianMixture): The GaussianMixture instance to be tested.
    
    This function checks that the `n_iter_` attribute of the estimator, which represents the number of iterations performed during fitting, is equal to the `max_iter` parameter set by the user. This ensures that the fitting process stops after the specified number of
    """

    # check that n_iter is the number of iteration performed.
    rng = np.random.RandomState(0)
    X = rng.rand(10, 5)
    max_iter = 1
    estimator.set_params(max_iter=max_iter)
    estimator.fit(X)
    assert estimator.n_iter_ == max_iter
