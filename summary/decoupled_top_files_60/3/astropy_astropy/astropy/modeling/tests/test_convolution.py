# Licensed under a 3-clause BSD style license - see LICENSE.rst
# pylint: disable=invalid-name
import numpy as np
import pytest

from astropy.convolution import convolve_models_fft
from astropy.modeling.models import Const1D, Const2D
from astropy.utils.compat.optional_deps import HAS_SCIPY


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy")
def test_clear_cache():
    """
    Clear the cache of a convolution model.
    
    This function clears the cached properties of a convolution model, ensuring that the next computation will recompute the cached values.
    
    Parameters:
    model (Model): The convolution model whose cache needs to be cleared.
    
    Returns:
    None: This function does not return any value. It modifies the input model in place.
    """

    m1 = Const1D()
    m2 = Const1D()

    model = convolve_models_fft(m1, m2, (-1, 1), 0.01)
    assert model._kwargs is None
    assert model._convolution is None

    results = model(0)
    assert results.all() == np.array([1.0]).all()
    assert model._kwargs is not None
    assert model._convolution is not None

    model.clear_cache()
    assert model._kwargs is None
    assert model._convolution is None


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy")
def test_input_shape_1d():
    m1 = Const1D()
    m2 = Const1D()

    model = convolve_models_fft(m1, m2, (-1, 1), 0.01)

    results = model(0)
    assert results.shape == (1,)

    x = np.arange(-1, 1, 0.1)
    results = model(x)
    assert results.shape == x.shape


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy")
def test_input_shape_2d():
    m1 = Const2D()
    m2 = Const2D()

    model = convolve_models_fft(m1, m2, ((-1, 1), (-1, 1)), 0.01)

    results = model(0, 0)
    assert results.shape == (1,)

    x = np.arange(-1, 1, 0.1)
    results = model(x, 0)
    assert results.shape == x.shape
    results = model(0, x)
    assert results.shape == x.shape

    grid = np.meshgrid(x, x)
    results = model(*grid)
    assert results.shape == grid[0].shape
    assert results.shape == grid[1].shape


@pytest.mark.skipif(not HAS_SCIPY, reason="requires scipy")
def test__convolution_inputs():
    """
    Tests the `_convolution_inputs` method of a convolution model.
    
    This function checks the behavior of the `_convolution_inputs` method for different input scenarios. It verifies the method's ability to handle scalar inputs, multiple inputs, and different grid shapes.
    
    Parameters:
    - `m1`: A 2D constant model.
    - `m2`: Another 2D constant model.
    - `grid0`: A meshgrid representing the first set of coordinates.
    - `grid1`: A meshgrid representing
    """

    m1 = Const2D()
    m2 = Const2D()

    model = convolve_models_fft(m1, m2, ((-1, 1), (-1, 1)), 0.01)

    x = np.arange(-1, 1, 0.1)
    y = np.arange(-2, 2, 0.1)
    grid0 = np.meshgrid(x, x)
    grid1 = np.meshgrid(y, y)

    # scalar inputs
    assert (np.array([1]), (1,)) == model._convolution_inputs(1)

    # Multiple inputs
    assert np.all(
        model._convolution_inputs(*grid0)[0]
        == np.reshape([grid0[0], grid0[1]], (2, -1)).T
    )
    assert model._convolution_inputs(*grid0)[1] == grid0[0].shape
    assert np.all(
        model._convolution_inputs(*grid1)[0]
        == np.reshape([grid1[0], grid1[1]], (2, -1)).T
    )
    assert model._convolution_inputs(*grid1)[1] == grid1[0].shape

    # Error
    with pytest.raises(ValueError, match=r"Values have differing shapes"):
        model._convolution_inputs(grid0[0], grid1[1])
