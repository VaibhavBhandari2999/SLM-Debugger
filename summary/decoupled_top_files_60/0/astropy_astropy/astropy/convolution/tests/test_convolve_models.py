# Licensed under a 3-clause BSD style license - see LICENSE.rst

import math

import pytest

import numpy as np
from numpy.testing import assert_allclose, assert_almost_equal

from astropy.convolution.convolve import convolve, convolve_fft, convolve_models
from astropy.modeling import fitting, models
from astropy.utils.compat.optional_deps import HAS_SCIPY  # noqa
from astropy.utils.misc import NumpyRNGContext


class TestConvolve1DModels:
    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    @pytest.mark.skipif('not HAS_SCIPY')
    def test_is_consistency_with_astropy_convolution(self, mode):
        """
        Tests the consistency between custom convolution functions and the `convolve_models` function from Astropy.
        
        Parameters:
        mode (str): The convolution mode to be tested. This should be a valid mode supported by the `convolve_models` function in Astropy.
        
        Returns:
        None: This function asserts that the results from the custom convolution function match the results from `convolve_models` from Astropy. If the assertion fails, an error will be raised.
        
        Key Steps:
        1. Defines a Gaussian
        """

        kernel = models.Gaussian1D(1, 0, 1)
        model = models.Gaussian1D(1, 0, 1)
        model_conv = convolve_models(model, kernel, mode=mode)
        x = np.arange(-5, 6)
        ans = eval(f"{mode}(model(x), kernel(x))")

        assert_allclose(ans, model_conv(x), atol=1e-5)

    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    @pytest.mark.skipif('not HAS_SCIPY')
    def test_against_scipy(self, mode):
        from scipy.signal import fftconvolve

        kernel = models.Gaussian1D(1, 0, 1)
        model = models.Gaussian1D(1, 0, 1)
        model_conv = convolve_models(model, kernel, mode=mode)
        x = np.arange(-5, 6)
        ans = fftconvolve(kernel(x), model(x), mode='same')

        assert_allclose(ans, model_conv(x) * kernel(x).sum(), atol=1e-5)

    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    @pytest.mark.skipif('not HAS_SCIPY')
    def test_against_scipy_with_additional_keywords(self, mode):
        from scipy.signal import fftconvolve

        kernel = models.Gaussian1D(1, 0, 1)
        model = models.Gaussian1D(1, 0, 1)
        model_conv = convolve_models(model, kernel, mode=mode,
                                     normalize_kernel=False)
        x = np.arange(-5, 6)
        ans = fftconvolve(kernel(x), model(x), mode='same')

        assert_allclose(ans, model_conv(x), atol=1e-5)

    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    def test_sum_of_gaussians(self, mode):
        """
        Test that convolving N(a, b) with N(c, d) gives N(a + c, b + d),
        where N(., .) stands for Gaussian probability density function,
        in which a and c are their means and b and d are their variances.
        """

        kernel = models.Gaussian1D(1 / math.sqrt(2 * np.pi), 1, 1)
        model = models.Gaussian1D(1 / math.sqrt(2 * np.pi), 3, 1)
        model_conv = convolve_models(model, kernel, mode=mode,
                                     normalize_kernel=False)
        ans = models.Gaussian1D(1 / (2 * math.sqrt(np.pi)), 4, np.sqrt(2))
        x = np.arange(-5, 6)

        assert_allclose(ans(x), model_conv(x), atol=1e-3)

    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    def test_convolve_box_models(self, mode):
        """
        Convolve two 1D box models using the specified convolution mode.
        
        Parameters
        ----------
        model : `~astropy.modeling.Model`
        The input model to be convolved.
        kernel : `~astropy.modeling.Model`
        The kernel model used for convolution.
        mode : str
        The convolution mode, which can be one of 'convolve', 'convolve_no_shift', or 'convolve_no_shift_no_overlap'.
        
        Returns
        -------
        convolved_model : `~astropy.modeling
        """

        kernel = models.Box1D()
        model = models.Box1D()
        model_conv = convolve_models(model, kernel, mode=mode)
        x = np.linspace(-1, 1, 99)
        ans = (x + 1) * (x < 0) + (-x + 1) * (x >= 0)

        assert_allclose(ans, model_conv(x), atol=1e-3)

    @pytest.mark.parametrize('mode', ['convolve_fft', 'convolve'])
    @pytest.mark.skipif('not HAS_SCIPY')
    def test_fitting_convolve_models(self, mode):
        """
        test that a convolve model can be fitted
        """
        b1 = models.Box1D()
        g1 = models.Gaussian1D()

        x = np.linspace(-5, 5, 99)
        fake_model = models.Gaussian1D(amplitude=10)
        with NumpyRNGContext(123):
            fake_data = fake_model(x) + np.random.normal(size=len(x))

        init_model = convolve_models(b1, g1, mode=mode, normalize_kernel=False)
        fitter = fitting.LevMarLSQFitter()
        fitted_model = fitter(init_model, x, fake_data)

        me = np.mean(fitted_model(x) - fake_data)
        assert_almost_equal(me, 0.0, decimal=2)
