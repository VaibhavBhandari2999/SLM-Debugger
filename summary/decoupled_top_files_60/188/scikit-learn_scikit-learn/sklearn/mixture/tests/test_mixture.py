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
    Test that the `n_iter_` attribute is set to the number of iterations performed.
    
    Parameters:
    estimator (GaussianMixture): The GaussianMixture instance to test.
    
    This function checks that the `n_iter_` attribute of the provided GaussianMixture instance is set to the number of iterations performed during fitting, ensuring that the model has completed the specified number of iterations.
    """

    # check that n_iter is the number of iteration performed.
    rng = np.random.RandomState(0)
    X = rng.rand(10, 5)
    max_iter = 1
    estimator.set_params(max_iter=max_iter)
    estimator.fit(X)
    assert estimator.n_iter_ == max_iter
