# Licensed under a 3-clause BSD style license - see LICENSE.rst


import os
import pickle

import numpy as np
from numpy.testing import assert_array_almost_equal

from ...utils.data import get_pkg_data_contents, get_pkg_data_fileobj
from ...utils.misc import NumpyRNGContext
from ...io import fits
from ... import wcs


def test_basic():
    """
    Test basic pickling of a WCS object.
    
    This function creates a WCS object, pickles it, and then unpickles it to
    ensure that the object can be serialized and deserialized without loss of
    information.
    
    Parameters:
    None
    
    Returns:
    None
    """

    wcs1 = wcs.WCS()
    s = pickle.dumps(wcs1)
    wcs2 = pickle.loads(s)


def test_dist():
    with get_pkg_data_fileobj(
            os.path.join("data", "dist.fits"), encoding='binary') as test_file:
        hdulist = fits.open(test_file)
        wcs1 = wcs.WCS(hdulist[0].header, hdulist)
        assert wcs1.det2im2 is not None
        s = pickle.dumps(wcs1)
        wcs2 = pickle.loads(s)

        with NumpyRNGContext(123456789):
            x = np.random.rand(2 ** 16, wcs1.wcs.naxis)
            world1 = wcs1.all_pix2world(x, 1)
            world2 = wcs2.all_pix2world(x, 1)

        assert_array_almost_equal(world1, world2)


def test_sip():
    with get_pkg_data_fileobj(
            os.path.join("data", "sip.fits"), encoding='binary') as test_file:
        hdulist = fits.open(test_file, ignore_missing_end=True)
        wcs1 = wcs.WCS(hdulist[0].header)
        assert wcs1.sip is not None
        s = pickle.dumps(wcs1)
        wcs2 = pickle.loads(s)

        with NumpyRNGContext(123456789):
            x = np.random.rand(2 ** 16, wcs1.wcs.naxis)
            world1 = wcs1.all_pix2world(x, 1)
            world2 = wcs2.all_pix2world(x, 1)

        assert_array_almost_equal(world1, world2)


def test_sip2():
    """
    Test the SIP (Simple Image Polynomial) support in WCS.
    
    This function reads a FITS file containing a SIP WCS, serializes the WCS object using pickle, and then deserializes it to ensure that the transformation between pixel and world coordinates remains consistent before and after serialization. The function uses a random set of pixel coordinates to perform the transformation and checks if the results are almost equal using `assert_array_almost_equal`.
    
    Parameters:
    None
    
    Returns:
    None
    """

    with get_pkg_data_fileobj(
            os.path.join("data", "sip2.fits"), encoding='binary') as test_file:
        hdulist = fits.open(test_file, ignore_missing_end=True)
        wcs1 = wcs.WCS(hdulist[0].header)
        assert wcs1.sip is not None
        s = pickle.dumps(wcs1)
        wcs2 = pickle.loads(s)

        with NumpyRNGContext(123456789):
            x = np.random.rand(2 ** 16, wcs1.wcs.naxis)
            world1 = wcs1.all_pix2world(x, 1)
            world2 = wcs2.all_pix2world(x, 1)

        assert_array_almost_equal(world1, world2)


def test_wcs():
    header = get_pkg_data_contents(
        os.path.join("data", "outside_sky.hdr"), encoding='binary')

    wcs1 = wcs.WCS(header)
    s = pickle.dumps(wcs1)
    wcs2 = pickle.loads(s)

    with NumpyRNGContext(123456789):
        x = np.random.rand(2 ** 16, wcs1.wcs.naxis)
        world1 = wcs1.all_pix2world(x, 1)
        world2 = wcs2.all_pix2world(x, 1)

    assert_array_almost_equal(world1, world2)


class Sub(wcs.WCS):
    def __init__(self, *args, **kwargs):
        self.foo = 42


def test_subclass():
    """
    Test subclass functionality.
    
    This function serializes and deserializes an instance of a subclass and checks if the subclass instance is properly restored with the correct attributes.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Attributes:
    wcs (Sub): An instance of the subclass.
    s (bytes): The serialized form of the subclass instance.
    wcs2 (Sub): The deserialized subclass instance.
    
    Assertions:
    - The deserialized instance should be an instance of the subclass.
    - The '
    """

    wcs = Sub()
    s = pickle.dumps(wcs)
    wcs2 = pickle.loads(s)

    assert isinstance(wcs2, Sub)
    assert wcs.foo == 42
    assert wcs2.foo == 42
    assert wcs2.wcs is not None
