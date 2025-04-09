# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest

import numpy as np
from numpy.testing import assert_almost_equal
from numpy.testing import assert_allclose

from ...utils.data import get_pkg_data_contents, get_pkg_data_filename
from ...time import Time
from ... import units as u

from ..wcs import WCS, Sip, WCSSUB_LONGITUDE, WCSSUB_LATITUDE
from ..utils import (proj_plane_pixel_scales, proj_plane_pixel_area,
                     is_proj_plane_distorted,
                     non_celestial_pixel_scales, wcs_to_celestial_frame,
                     celestial_frame_to_wcs, skycoord_to_pixel,
                     pixel_to_skycoord, custom_wcs_to_frame_mappings,
                     custom_frame_to_wcs_mappings, add_stokes_axis_to_wcs)


def test_wcs_dropping():
    """
    Drops an axis from a 4-dimensional World Coordinate System (WCS) transformation.
    
    This function takes a 4-dimensional WCS object and drops one of its axes,
    modifying the pixel-to-world coordinate transformation matrix (PC) or CD matrix
    accordingly. The function supports both PC and CD matrices.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses the `dropaxis` method of the WCS object to drop an axis.
    -
    """

    wcs = WCS(naxis=4)
    wcs.wcs.pc = np.zeros([4, 4])
    np.fill_diagonal(wcs.wcs.pc, np.arange(1, 5))
    pc = wcs.wcs.pc  # for later use below

    dropped = wcs.dropaxis(0)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([2, 3, 4]))
    dropped = wcs.dropaxis(1)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 3, 4]))
    dropped = wcs.dropaxis(2)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 2, 4]))
    dropped = wcs.dropaxis(3)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 2, 3]))

    wcs = WCS(naxis=4)
    wcs.wcs.cd = pc

    dropped = wcs.dropaxis(0)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([2, 3, 4]))
    dropped = wcs.dropaxis(1)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 3, 4]))
    dropped = wcs.dropaxis(2)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 2, 4]))
    dropped = wcs.dropaxis(3)
    assert np.all(dropped.wcs.get_pc().diagonal() == np.array([1, 2, 3]))


def test_wcs_swapping():
    """
    Swaps axes of a 4-dimensional WCS object and checks the resulting PC matrix.
    
    This function tests the `swapaxes` method of a World Coordinate System (WCS) object with different axis swaps. It initializes a 4D WCS object with specific PC matrices and verifies that after swapping axes, the diagonal elements of the PC matrix are correctly rearranged according to the specified axis swaps.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `WCS
    """

    wcs = WCS(naxis=4)
    wcs.wcs.pc = np.zeros([4, 4])
    np.fill_diagonal(wcs.wcs.pc, np.arange(1, 5))
    pc = wcs.wcs.pc  # for later use below

    swapped = wcs.swapaxes(0, 1)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([2, 1, 3, 4]))
    swapped = wcs.swapaxes(0, 3)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([4, 2, 3, 1]))
    swapped = wcs.swapaxes(2, 3)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([1, 2, 4, 3]))

    wcs = WCS(naxis=4)
    wcs.wcs.cd = pc

    swapped = wcs.swapaxes(0, 1)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([2, 1, 3, 4]))
    swapped = wcs.swapaxes(0, 3)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([4, 2, 3, 1]))
    swapped = wcs.swapaxes(2, 3)
    assert np.all(swapped.wcs.get_pc().diagonal() == np.array([1, 2, 4, 3]))


@pytest.mark.parametrize('ndim', (2, 3))
def test_add_stokes(ndim):
    """
    Add a Stokes axis to a WCS object.
    
    This function takes a WCS object with `ndim` dimensions and returns a new WCS object with an additional Stokes axis inserted at the specified position. The function iterates over the dimensions of the input WCS object and checks if the output WCS object has the correct number of axes and the correct type of the added axis.
    
    Parameters:
    -----------
    ndim : int
    Number of dimensions of the input WCS object.
    
    Returns:
    --------
    """

    wcs = WCS(naxis=ndim)

    for ii in range(ndim + 1):
        outwcs = add_stokes_axis_to_wcs(wcs, ii)
        assert outwcs.wcs.naxis == ndim + 1
        assert outwcs.wcs.ctype[ii] == 'STOKES'
        assert outwcs.wcs.cname[ii] == 'STOKES'


def test_slice():
    """
    Slices a WCS object along specified axes.
    
    This function takes a World Coordinate System (WCS) object and slices it along specified axes. The slicing operation modifies the WCS object's attributes such as `crpix` and `_naxis` to reflect the new dimensions of the sliced array. It also ensures that the CRPIX (CR Pixel) maps correctly to CRVAL (CR Value).
    
    Parameters:
    mywcs (WCS): The original WCS object to be sliced.
    
    Returns:
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.crval = [1, 1]
    mywcs.wcs.cdelt = [0.1, 0.1]
    mywcs.wcs.crpix = [1, 1]
    mywcs._naxis = [1000, 500]
    pscale = 0.1 # from cdelt

    slice_wcs = mywcs.slice([slice(1, None), slice(0, None)])
    assert np.all(slice_wcs.wcs.crpix == np.array([1, 0]))
    assert slice_wcs._naxis == [1000, 499]

    # test that CRPIX maps to CRVAL:
    assert_allclose(
        slice_wcs.wcs_pix2world(*slice_wcs.wcs.crpix, 1),
        slice_wcs.wcs.crval, rtol=0.0, atol=1e-6 * pscale
    )

    slice_wcs = mywcs.slice([slice(1, None, 2), slice(0, None, 4)])
    assert np.all(slice_wcs.wcs.crpix == np.array([0.625, 0.25]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.4, 0.2]))
    assert slice_wcs._naxis == [250, 250]

    slice_wcs = mywcs.slice([slice(None, None, 2), slice(0, None, 2)])
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.2, 0.2]))
    assert slice_wcs._naxis == [500, 250]

    # Non-integral values do not alter the naxis attribute
    slice_wcs = mywcs.slice([slice(50.), slice(20.)])
    assert slice_wcs._naxis == [1000, 500]
    slice_wcs = mywcs.slice([slice(50.), slice(20)])
    assert slice_wcs._naxis == [20, 500]
    slice_wcs = mywcs.slice([slice(50), slice(20.5)])
    assert slice_wcs._naxis == [1000, 50]


def test_slice_with_sip():
    """
    Test slicing a WCS object with SIP distortion.
    
    This function slices a World Coordinate System (WCS) object with SIP (Simple Image Polynomial) distortion and checks if the CRPIX (CR Pixel) coordinate maps correctly to CRVAL (CR Value) after slicing. The slicing is performed using different step sizes and the accuracy of the transformation is verified.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `WCS`: Constructs a WCS object with specified crval
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.crval = [1, 1]
    mywcs.wcs.cdelt = [0.1, 0.1]
    mywcs.wcs.crpix = [1, 1]
    mywcs._naxis = [1000, 500]
    mywcs.wcs.ctype = ['RA---TAN-SIP', 'DEC--TAN-SIP']
    a = np.array(
        [[0, 0, 5.33092692e-08, 3.73753773e-11, -2.02111473e-13],
         [0, 2.44084308e-05, 2.81394789e-11, 5.17856895e-13, 0.0],
         [-2.41334657e-07, 1.29289255e-10, 2.35753629e-14, 0.0, 0.0],
         [-2.37162007e-10, 5.43714947e-13, 0.0, 0.0, 0.0],
         [ -2.81029767e-13, 0.0, 0.0, 0.0, 0.0]]
    )
    b = np.array(
        [[0, 0, 2.99270374e-05, -2.38136074e-10, 7.23205168e-13],
         [0, -1.71073858e-07, 6.31243431e-11, -5.16744347e-14, 0.0],
         [6.95458963e-06, -3.08278961e-10, -1.75800917e-13, 0.0, 0.0],
         [3.51974159e-11, 5.60993016e-14, 0.0, 0.0, 0.0],
         [-5.92438525e-13, 0.0, 0.0, 0.0, 0.0]]
    )
    mywcs.sip = Sip(a, b, None, None, mywcs.wcs.crpix)
    mywcs.wcs.set()
    pscale = 0.1 # from cdelt

    slice_wcs = mywcs.slice([slice(1, None), slice(0, None)])
    # test that CRPIX maps to CRVAL:
    assert_allclose(
        slice_wcs.all_pix2world(*slice_wcs.wcs.crpix, 1),
        slice_wcs.wcs.crval, rtol=0.0, atol=1e-6 * pscale
    )

    slice_wcs = mywcs.slice([slice(1, None, 2), slice(0, None, 4)])
    # test that CRPIX maps to CRVAL:
    assert_allclose(
        slice_wcs.all_pix2world(*slice_wcs.wcs.crpix, 1),
        slice_wcs.wcs.crval, rtol=0.0, atol=1e-6 * pscale
    )


def test_slice_getitem():
    """
    Extracts a subset of a WCS object using slicing.
    
    This function demonstrates how to extract a subset of a World Coordinate System (WCS) object using slicing operations. The slicing can be applied to both axes of the WCS object, and the resulting subset is a new WCS object with updated reference pixel coordinates (`crpix`) and pixel scale (`cdelt`).
    
    Parameters:
    None
    
    Returns:
    None
    
    Examples:
    - Slicing a 2D WCS object with `
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.crval = [1, 1]
    mywcs.wcs.cdelt = [0.1, 0.1]
    mywcs.wcs.crpix = [1, 1]

    slice_wcs = mywcs[1::2, 0::4]
    assert np.all(slice_wcs.wcs.crpix == np.array([0.625, 0.25]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.4, 0.2]))

    mywcs.wcs.crpix = [2, 2]
    slice_wcs = mywcs[1::2, 0::4]
    assert np.all(slice_wcs.wcs.crpix == np.array([0.875, 0.75]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.4, 0.2]))

    # Default: numpy order
    slice_wcs = mywcs[1::2]
    assert np.all(slice_wcs.wcs.crpix == np.array([2, 0.75]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.1, 0.2]))


def test_slice_fitsorder():
    """
    Test slicing a WCS object.
    
    This function tests the slicing functionality of a World Coordinate System (WCS) object. It creates a WCS object with specific reference values and cdelt (change in degrees per pixel). The function then slices the WCS object using different slice parameters and checks if the resulting WCS object has the correct crpix (crpix is the reference pixel coordinate) and cdelt values.
    
    Parameters:
    None
    
    Returns:
    None
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.crval = [1, 1]
    mywcs.wcs.cdelt = [0.1, 0.1]
    mywcs.wcs.crpix = [1, 1]

    slice_wcs = mywcs.slice([slice(1, None), slice(0, None)], numpy_order=False)
    assert np.all(slice_wcs.wcs.crpix == np.array([0, 1]))

    slice_wcs = mywcs.slice([slice(1, None, 2), slice(0, None, 4)], numpy_order=False)
    assert np.all(slice_wcs.wcs.crpix == np.array([0.25, 0.625]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.2, 0.4]))

    slice_wcs = mywcs.slice([slice(1, None, 2)], numpy_order=False)
    assert np.all(slice_wcs.wcs.crpix == np.array([0.25, 1]))
    assert np.all(slice_wcs.wcs.cdelt == np.array([0.2, 0.1]))


def test_invalid_slice():
    """
    Raise ValueError when attempting to slice a WCS object.
    
    This function tests that slicing a WCS object raises a ValueError,
    indicating that downsampling a WCS with indexing is not allowed. Instead,
    use `wcs.sub` or `wcs.dropaxis` to remove axes.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If an attempt is made to slice the WCS object.
    
    Example Usage:
    >>> test_invalid_slice()
    """

    mywcs = WCS(naxis=2)

    with pytest.raises(ValueError) as exc:
        mywcs[0]
    assert exc.value.args[0] == ("Cannot downsample a WCS with indexing.  Use "
                                 "wcs.sub or wcs.dropaxis if you want to remove "
                                 "axes.")

    with pytest.raises(ValueError) as exc:
        mywcs[0, ::2]
    assert exc.value.args[0] == ("Cannot downsample a WCS with indexing.  Use "
                                 "wcs.sub or wcs.dropaxis if you want to remove "
                                 "axes.")


def test_axis_names():
    """
    Test the axis type names of a World Coordinate System (WCS) object.
    
    This function checks the behavior of the `axis_type_names` attribute of a
    WCS object when setting the `ctype` and `cname` attributes. It ensures that
    the `axis_type_names` are correctly updated based on the provided axis
    types.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses the `WCS` class from the `
    """

    mywcs = WCS(naxis=4)
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN', 'VOPT-LSR', 'STOKES']

    assert mywcs.axis_type_names == ['RA', 'DEC', 'VOPT', 'STOKES']

    mywcs.wcs.cname = ['RA', 'DEC', 'VOPT', 'STOKES']

    assert mywcs.axis_type_names == ['RA', 'DEC', 'VOPT', 'STOKES']


def test_celestial():
    """
    Generate a celestial coordinate system from a multi-dimensional WCS object.
    
    This function extracts the celestial components (RA and DEC) from a given
    World Coordinate System (WCS) object with four dimensions. It returns a new
    WCS object that only contains the celestial coordinates.
    
    Parameters:
    mywcs (WCS): A WCS object with four dimensions, containing information
    about the celestial coordinates and other axes.
    
    Returns:
    cel (WCS): A new WCS object that only
    """

    mywcs = WCS(naxis=4)
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN', 'VOPT', 'STOKES']
    cel = mywcs.celestial
    assert tuple(cel.wcs.ctype) == ('RA---TAN', 'DEC--TAN')
    assert cel.axis_type_names == ['RA', 'DEC']


def test_wcs_to_celestial_frame():
    """
    Determine the celestial frame corresponding to a given WCS object.
    
    This function maps the `WCS` object's properties to an appropriate
    `astropy.coordinates` celestial frame. It handles various types of
    coordinate systems including ICRS, FK5, FK4, Galactic, ITRS, and
    offset coordinates. The function raises a `ValueError` if the WCS
    object does not correspond to a recognized celestial frame.
    
    Parameters:
    - mywcs (W
    """


    # Import astropy.coordinates here to avoid circular imports
    from ...coordinates.builtin_frames import ICRS, ITRS, FK5, FK4, Galactic

    mywcs = WCS(naxis=2)
    mywcs.wcs.set()
    with pytest.raises(ValueError) as exc:
        assert wcs_to_celestial_frame(mywcs) is None
    assert exc.value.args[0] == "Could not determine celestial frame corresponding to the specified WCS object"

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['XOFFSET', 'YOFFSET']
    mywcs.wcs.set()
    with pytest.raises(ValueError):
        assert wcs_to_celestial_frame(mywcs) is None

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, ICRS)

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    mywcs.wcs.equinox = 1987.
    mywcs.wcs.set()
    print(mywcs.to_header())
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, FK5)
    assert frame.equinox == Time(1987., format='jyear')

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    mywcs.wcs.equinox = 1982
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, FK4)
    assert frame.equinox == Time(1982., format='byear')

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['GLON-SIN', 'GLAT-SIN']
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, Galactic)

    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['TLON-CAR', 'TLAT-CAR']
    mywcs.wcs.dateobs = '2017-08-17T12:41:04.430'
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, ITRS)
    assert frame.obstime == Time('2017-08-17T12:41:04.430')

    for equinox in [np.nan, 1987, 1982]:
        mywcs = WCS(naxis=2)
        mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
        mywcs.wcs.radesys = 'ICRS'
        mywcs.wcs.equinox = equinox
        mywcs.wcs.set()
        frame = wcs_to_celestial_frame(mywcs)
        assert isinstance(frame, ICRS)

    # Flipped order
    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['DEC--TAN', 'RA---TAN']
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, ICRS)

    # More than two dimensions
    mywcs = WCS(naxis=3)
    mywcs.wcs.ctype = ['DEC--TAN', 'VELOCITY', 'RA---TAN']
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, ICRS)

    mywcs = WCS(naxis=3)
    mywcs.wcs.ctype = ['GLAT-CAR', 'VELOCITY', 'GLON-CAR']
    mywcs.wcs.set()
    frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, Galactic)


def test_wcs_to_celestial_frame_extend():
    """
    Converts a World Coordinate System (WCS) object to a celestial frame.
    
    This function tests the conversion of a WCS object with specific offset types to a celestial frame. It first creates a WCS object with 'XOFFSET' and 'YOFFSET' types and attempts to convert it directly, expecting a ValueError. Then, it defines a custom frame `OffsetFrame` and a function `identify_offset` to map this frame to WCS objects with offset types. Using a context manager, it maps `
    """


    mywcs = WCS(naxis=2)
    mywcs.wcs.ctype = ['XOFFSET', 'YOFFSET']
    mywcs.wcs.set()
    with pytest.raises(ValueError):
        wcs_to_celestial_frame(mywcs)

    class OffsetFrame:
        pass

    def identify_offset(wcs):
        """
        Identify the offset frame.
        
        This function takes a `frame` object and returns a World Coordinate System (WCS) object representing an offset frame. If the input `frame` is an instance of `OffsetFrame`, a WCS object with types 'XOFFSET' and 'YOFFSET' is returned.
        
        Parameters:
        frame (object): The input frame object.
        projection (Optional[WCS]): An optional WCS projection to be used.
        
        Returns:
        WCS: A World Coordinate System
        """

        if wcs.wcs.ctype[0].endswith('OFFSET') and wcs.wcs.ctype[1].endswith('OFFSET'):
            return OffsetFrame()

    with custom_wcs_to_frame_mappings(identify_offset):
        frame = wcs_to_celestial_frame(mywcs)
    assert isinstance(frame, OffsetFrame)

    # Check that things are back to normal after the context manager
    with pytest.raises(ValueError):
        wcs_to_celestial_frame(mywcs)


def test_celestial_frame_to_wcs():
    """
    Converts a CelestialFrame to a WCS object.
    
    Parameters:
    frame (BaseCoordinateFrame): The input celestial frame to convert.
    
    Returns:
    astropy.wcs.WCS: The resulting WCS object corresponding to the input frame.
    
    Raises:
    ValueError: If the input frame is not a recognized celestial frame.
    
    Examples:
    >>> from astropy.coordinates import ICRS, FK5, FK4, FK4NoETerms, Galactic, ITRS
    >>>
    """


    # Import astropy.coordinates here to avoid circular imports
    from ...coordinates import ICRS, ITRS, FK5, FK4, FK4NoETerms, Galactic, BaseCoordinateFrame

    class FakeFrame(BaseCoordinateFrame):
        pass

    frame = FakeFrame()
    with pytest.raises(ValueError) as exc:
        celestial_frame_to_wcs(frame)
    assert exc.value.args[0] == ("Could not determine WCS corresponding to "
                                 "the specified coordinate frame.")

    frame = ICRS()
    mywcs = celestial_frame_to_wcs(frame)
    mywcs.wcs.set()
    assert tuple(mywcs.wcs.ctype) == ('RA---TAN', 'DEC--TAN')
    assert mywcs.wcs.radesys == 'ICRS'
    assert np.isnan(mywcs.wcs.equinox)
    assert mywcs.wcs.lonpole == 180
    assert mywcs.wcs.latpole == 0

    frame = FK5(equinox='J1987')
    mywcs = celestial_frame_to_wcs(frame)
    assert tuple(mywcs.wcs.ctype) == ('RA---TAN', 'DEC--TAN')
    assert mywcs.wcs.radesys == 'FK5'
    assert mywcs.wcs.equinox == 1987.

    frame = FK4(equinox='B1982')
    mywcs = celestial_frame_to_wcs(frame)
    assert tuple(mywcs.wcs.ctype) == ('RA---TAN', 'DEC--TAN')
    assert mywcs.wcs.radesys == 'FK4'
    assert mywcs.wcs.equinox == 1982.

    frame = FK4NoETerms(equinox='B1982')
    mywcs = celestial_frame_to_wcs(frame)
    assert tuple(mywcs.wcs.ctype) == ('RA---TAN', 'DEC--TAN')
    assert mywcs.wcs.radesys == 'FK4-NO-E'
    assert mywcs.wcs.equinox == 1982.

    frame = Galactic()
    mywcs = celestial_frame_to_wcs(frame)
    assert tuple(mywcs.wcs.ctype) == ('GLON-TAN', 'GLAT-TAN')
    assert mywcs.wcs.radesys == ''
    assert np.isnan(mywcs.wcs.equinox)

    frame = Galactic()
    mywcs = celestial_frame_to_wcs(frame, projection='CAR')
    assert tuple(mywcs.wcs.ctype) == ('GLON-CAR', 'GLAT-CAR')
    assert mywcs.wcs.radesys == ''
    assert np.isnan(mywcs.wcs.equinox)

    frame = Galactic()
    mywcs = celestial_frame_to_wcs(frame, projection='CAR')
    mywcs.wcs.crval = [100, -30]
    mywcs.wcs.set()
    assert_allclose((mywcs.wcs.lonpole, mywcs.wcs.latpole), (180, 60))

    frame = ITRS(obstime=Time('2017-08-17T12:41:04.43'))
    mywcs = celestial_frame_to_wcs(frame, projection='CAR')
    assert tuple(mywcs.wcs.ctype) == ('TLON-CAR', 'TLAT-CAR')
    assert mywcs.wcs.radesys == 'ITRS'
    assert mywcs.wcs.dateobs == '2017-08-17T12:41:04.430'

    frame = ITRS()
    mywcs = celestial_frame_to_wcs(frame, projection='CAR')
    assert tuple(mywcs.wcs.ctype) == ('TLON-CAR', 'TLAT-CAR')
    assert mywcs.wcs.radesys == 'ITRS'
    assert mywcs.wcs.dateobs == Time('J2000').utc.isot


def test_celestial_frame_to_wcs_extend():
    """
    Summary: This function tests the conversion of a custom celestial frame to a World Coordinate System (WCS) using the `celestial_frame_to_wcs` function.
    
    The function creates an instance of a custom frame called `OffsetFrame` and attempts to convert it to a WCS without a custom mapping, expecting a ValueError. It then uses a context manager to map the `OffsetFrame` to a custom WCS with `identify_offset` function, successfully converting the frame and verifying the output. After exiting
    """


    class OffsetFrame:
        pass

    frame = OffsetFrame()

    with pytest.raises(ValueError):
        celestial_frame_to_wcs(frame)

    def identify_offset(frame, projection=None):
        if isinstance(frame, OffsetFrame):
            wcs = WCS(naxis=2)
            wcs.wcs.ctype = ['XOFFSET', 'YOFFSET']
            return wcs

    with custom_frame_to_wcs_mappings(identify_offset):
        mywcs = celestial_frame_to_wcs(frame)
    assert tuple(mywcs.wcs.ctype) == ('XOFFSET', 'YOFFSET')

    # Check that things are back to normal after the context manager
    with pytest.raises(ValueError):
        celestial_frame_to_wcs(frame)


def test_pixscale_nodrop():
    """
    Calculate the projected plane pixel scales for a given World Coordinate System (WCS).
    
    Parameters:
    mywcs (astropy.wcs.WCS): The World Coordinate System object containing the CD matrix.
    
    Returns:
    tuple: A tuple of two floats representing the pixel scale in the RA and DEC directions.
    
    Notes:
    - The function uses the `proj_plane_pixel_scales` method from the `astropy.wcs` module to calculate the pixel scales.
    - The input `my
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.cdelt = [0.1, 0.2]
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert_almost_equal(proj_plane_pixel_scales(mywcs), (0.1, 0.2))

    mywcs.wcs.cdelt = [-0.1, 0.2]
    assert_almost_equal(proj_plane_pixel_scales(mywcs), (0.1, 0.2))


def test_pixscale_withdrop():
    """
    Calculate the pixel scales on the projection plane for a given celestial WCS.
    
    Parameters:
    mywcs (WCS object): A World Coordinate System (WCS) object with celestial axes.
    
    Returns:
    tuple: A tuple containing the pixel scales along the RA and DEC axes.
    
    Notes:
    - The function uses the `proj_plane_pixel_scales` method from the `astropy.wcs` module to calculate the pixel scales.
    - The input `mywcs` should have its
    """

    mywcs = WCS(naxis=3)
    mywcs.wcs.cdelt = [0.1, 0.2, 1]
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN', 'VOPT']
    assert_almost_equal(proj_plane_pixel_scales(mywcs.celestial), (0.1, 0.2))

    mywcs.wcs.cdelt = [-0.1, 0.2, 1]
    assert_almost_equal(proj_plane_pixel_scales(mywcs.celestial), (0.1, 0.2))


def test_pixscale_cd():
    """
    Calculate the pixel scales in degrees per pixel along each axis.
    
    Args:
    mywcs (WCS object): A World Coordinate System (WCS) object containing the CD matrix.
    
    Returns:
    tuple: A tuple of two floats representing the pixel scale in degrees per pixel along the x-axis and y-axis respectively.
    
    Notes:
    - The function uses the `proj_plane_pixel_scales` method from the `astropy.wcs.utils` module to calculate the pixel scales.
    -
    """

    mywcs = WCS(naxis=2)
    mywcs.wcs.cd = [[-0.1, 0], [0, 0.2]]
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert_almost_equal(proj_plane_pixel_scales(mywcs), (0.1, 0.2))


@pytest.mark.parametrize('angle',
                         (30, 45, 60, 75))
def test_pixscale_cd_rotated(angle):
    """
    Calculate the pixel scale of a rotated CD matrix.
    
    Args:
    angle (float): The rotation angle in degrees.
    
    Returns:
    tuple: The projected plane pixel scales in RA and DEC directions.
    
    Notes:
    - The function uses the `WCS` class from the `astropy.wcs` module to create a world coordinate system with a rotated CD matrix.
    - The `cd` attribute of the `mywcs` object is set to a 2x2 array representing
    """

    mywcs = WCS(naxis=2)
    rho = np.radians(angle)
    scale = 0.1
    mywcs.wcs.cd = [[scale * np.cos(rho), -scale * np.sin(rho)],
                    [scale * np.sin(rho), scale * np.cos(rho)]]
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert_almost_equal(proj_plane_pixel_scales(mywcs), (0.1, 0.1))


@pytest.mark.parametrize('angle',
                         (30, 45, 60, 75))
def test_pixscale_pc_rotated(angle):
    """
    Calculate the pixel scales of a rotated projection plane.
    
    Args:
    angle (float): The rotation angle in degrees.
    
    Returns:
    tuple: A tuple containing the pixel scales along the RA and DEC axes.
    
    Notes:
    - The function uses the `WCS` class from the `astropy.wcs` module to define a world coordinate system with a rotated projection plane.
    - The `cdelt` attribute is set to define the pixel scale.
    - The `pc`
    """

    mywcs = WCS(naxis=2)
    rho = np.radians(angle)
    scale = 0.1
    mywcs.wcs.cdelt = [-scale, scale]
    mywcs.wcs.pc = [[np.cos(rho), -np.sin(rho)],
                    [np.sin(rho), np.cos(rho)]]
    mywcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert_almost_equal(proj_plane_pixel_scales(mywcs), (0.1, 0.1))


@pytest.mark.parametrize(('cdelt', 'pc', 'pccd'),
                         (([0.1, 0.2], np.eye(2), np.diag([0.1, 0.2])),
                          ([0.1, 0.2, 0.3], np.eye(3), np.diag([0.1, 0.2, 0.3])),
                          ([1, 1, 1], np.diag([0.1, 0.2, 0.3]), np.diag([0.1, 0.2, 0.3]))))
def test_pixel_scale_matrix(cdelt, pc, pccd):
    """
    Test the pixel scale matrix calculation.
    
    This function creates a World Coordinate System (WCS) object using the given `cdelt` (pixel scales in each axis), `pc` (position angle rotation matrix), and `pccd` (expected pixel scale matrix). It then compares the calculated pixel scale matrix with the expected one using `assert_almost_equal`.
    
    Parameters:
    cdelt (list or array-like): Pixel scales in each axis.
    pc (2D array-like): Position angle
    """


    mywcs = WCS(naxis=(len(cdelt)))
    mywcs.wcs.cdelt = cdelt
    mywcs.wcs.pc = pc

    assert_almost_equal(mywcs.pixel_scale_matrix, pccd)


@pytest.mark.parametrize(('ctype', 'cel'),
                         ((['RA---TAN', 'DEC--TAN'], True),
                          (['RA---TAN', 'DEC--TAN', 'FREQ'], False),
                          (['RA---TAN', 'FREQ'], False),))
def test_is_celestial(ctype, cel):
    """
    Check if the given coordinate types represent celestial coordinates.
    
    Parameters:
    -----------
    ctype : list of str
    A list containing the coordinate types (e.g., ['RA---TAN', 'DEC--TAN']).
    cel : bool
    Expected boolean value indicating whether the given coordinate types are celestial.
    
    Returns:
    --------
    None
    This function does not return any value. It asserts that the `is_celestial` attribute of the generated WCS object matches the
    """

    mywcs = WCS(naxis=len(ctype))
    mywcs.wcs.ctype = ctype

    assert mywcs.is_celestial == cel


@pytest.mark.parametrize(('ctype', 'cel'),
                         ((['RA---TAN', 'DEC--TAN'], True),
                          (['RA---TAN', 'DEC--TAN', 'FREQ'], True),
                          (['RA---TAN', 'FREQ'], False),))
def test_has_celestial(ctype, cel):
    """
    Check if the given World Coordinate System (WCS) has celestial coordinates.
    
    Parameters:
    -----------
    ctype : list of str
    The types of coordinate axes defined by the WCS.
    cel : bool
    Expected result indicating whether the WCS has celestial coordinates.
    
    Returns:
    --------
    None
    This function does not return any value. It asserts that the `has_celestial` attribute of the generated WCS object matches the expected boolean value.
    
    Usage:
    ------
    """

    mywcs = WCS(naxis=len(ctype))
    mywcs.wcs.ctype = ctype

    assert mywcs.has_celestial == cel


@pytest.mark.parametrize(('cdelt', 'pc', 'cd'),
                         ((np.array([0.1, 0.2]), np.eye(2), np.eye(2)),
                          (np.array([1, 1]), np.diag([0.1, 0.2]), np.eye(2)),
                          (np.array([0.1, 0.2]), np.eye(2), None),
                          (np.array([0.1, 0.2]), None, np.eye(2)),
                          ))
def test_noncelestial_scale(cdelt, pc, cd):
    """
    Calculate non-celestial pixel scales.
    
    This function computes the non-celestial pixel scales using the given
    CDelt, PC, and CD values in a WCS object. It sets the necessary WCS
    attributes and then uses the `non_celestial_pixel_scales` function to
    determine the pixel scales.
    
    Parameters:
    -----------
    cdelt : array-like
    The pixel scale in degrees along each axis.
    pc : array-like, optional
    The
    """


    mywcs = WCS(naxis=2)
    if cd is not None:
        mywcs.wcs.cd = cd
    if pc is not None:
        mywcs.wcs.pc = pc
    mywcs.wcs.cdelt = cdelt

    mywcs.wcs.ctype = ['RA---TAN', 'FREQ']

    ps = non_celestial_pixel_scales(mywcs)

    assert_almost_equal(ps.to_value(u.deg), np.array([0.1, 0.2]))


@pytest.mark.parametrize('mode', ['all', 'wcs'])
def test_skycoord_to_pixel(mode):
    """
    Converts a SkyCoord object to pixel coordinates using the given WCS and mode.
    
    Parameters:
    -----------
    mode : str
    The mode for handling coordinate transformations.
    
    Returns:
    --------
    xp, yp : float
    The pixel coordinates corresponding to the reference SkyCoord.
    
    Notes:
    ------
    - Uses `astropy.coordinates.SkyCoord` for coordinate operations.
    - Utilizes `astropy.wcs.WCS` for defining the world coordinate system.
    -
    """


    # Import astropy.coordinates here to avoid circular imports
    from ...coordinates import SkyCoord

    header = get_pkg_data_contents('maps/1904-66_TAN.hdr', encoding='binary')
    wcs = WCS(header)

    ref = SkyCoord(0.1 * u.deg, -89. * u.deg, frame='icrs')

    xp, yp = skycoord_to_pixel(ref, wcs, mode=mode)

    # WCS is in FK5 so we need to transform back to ICRS
    new = pixel_to_skycoord(xp, yp, wcs, mode=mode).transform_to('icrs')

    assert_allclose(new.ra.degree, ref.ra.degree)
    assert_allclose(new.dec.degree, ref.dec.degree)

    # Make sure you can specify a different class using ``cls`` keyword
    class SkyCoord2(SkyCoord):
        pass

    new2 = pixel_to_skycoord(xp, yp, wcs, mode=mode,
                             cls=SkyCoord2).transform_to('icrs')

    assert new2.__class__ is SkyCoord2
    assert_allclose(new2.ra.degree, ref.ra.degree)
    assert_allclose(new2.dec.degree, ref.dec.degree)


def test_skycoord_to_pixel_swapped():
    """
    Test skycoord_to_pixel and pixel_to_skycoord with swapped axes in WCS.
    
    This function verifies that the `skycoord_to_pixel` and `pixel_to_skycoord`
    functions work correctly even when the axes are swapped in the WCS. It uses
    a specific header file to create a WCS object and its swapped version. The
    function compares the results of transforming a reference sky coordinate to
    pixel coordinates and back using both the original and swapped WCS objects.
    
    Parameters
    """


    # Regression test for a bug that caused skycoord_to_pixel and
    # pixel_to_skycoord to not work correctly if the axes were swapped in the
    # WCS.

    # Import astropy.coordinates here to avoid circular imports
    from ...coordinates import SkyCoord

    header = get_pkg_data_contents('maps/1904-66_TAN.hdr', encoding='binary')
    wcs = WCS(header)

    wcs_swapped = wcs.sub([WCSSUB_LATITUDE, WCSSUB_LONGITUDE])

    ref = SkyCoord(0.1 * u.deg, -89. * u.deg, frame='icrs')

    xp1, yp1 = skycoord_to_pixel(ref, wcs)
    xp2, yp2 = skycoord_to_pixel(ref, wcs_swapped)

    assert_allclose(xp1, xp2)
    assert_allclose(yp1, yp2)

    # WCS is in FK5 so we need to transform back to ICRS
    new1 = pixel_to_skycoord(xp1, yp1, wcs).transform_to('icrs')
    new2 = pixel_to_skycoord(xp1, yp1, wcs_swapped).transform_to('icrs')

    assert_allclose(new1.ra.degree, new2.ra.degree)
    assert_allclose(new1.dec.degree, new2.dec.degree)


def test_is_proj_plane_distorted():
    """
    Determine if a projection plane is distorted.
    
    This function checks whether the projection plane defined by the World Coordinate System (WCS) is distorted based on the CD matrix. A projection plane is considered undistorted if the CD matrix is nearly orthogonal.
    
    Parameters:
    wcs (astropy.wcs.WCS): The WCS object representing the projection plane.
    
    Returns:
    bool: True if the projection plane is distorted, False otherwise.
    
    Examples:
    >>> from astropy.wcs import
    """

    # non-orthogonal CD:
    wcs = WCS(naxis=2)
    wcs.wcs.cd = [[-0.1, 0], [0, 0.2]]
    wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert(is_proj_plane_distorted(wcs))

    # almost orthogonal CD:
    wcs.wcs.cd = [[0.1 + 2.0e-7, 1.7e-7], [1.2e-7, 0.1 - 1.3e-7]]
    assert(not is_proj_plane_distorted(wcs))

    # real case:
    header = get_pkg_data_filename('data/sip.fits')
    wcs = WCS(header)
    assert(is_proj_plane_distorted(wcs))


@pytest.mark.parametrize('mode', ['all', 'wcs'])
def test_skycoord_to_pixel_distortions(mode):
    """
    Converts a SkyCoord object to pixel coordinates using a World Coordinate System (WCS) with distortion corrections based on the specified mode. The function reads a FITS file containing the WCS information, transforms the reference coordinate to pixel coordinates, and then converts these pixel coordinates back to a SkyCoord object in the ICRS frame. The mode parameter determines how the distortions are applied during the transformation.
    
    Parameters:
    mode (str): The mode specifying how to handle distortions during the transformation.
    """


    # Import astropy.coordinates here to avoid circular imports
    from ...coordinates import SkyCoord

    header = get_pkg_data_filename('data/sip.fits')
    wcs = WCS(header)

    ref = SkyCoord(202.50 * u.deg, 47.19 * u.deg, frame='icrs')

    xp, yp = skycoord_to_pixel(ref, wcs, mode=mode)

    # WCS is in FK5 so we need to transform back to ICRS
    new = pixel_to_skycoord(xp, yp, wcs, mode=mode).transform_to('icrs')

    assert_allclose(new.ra.degree, ref.ra.degree)
    assert_allclose(new.dec.degree, ref.dec.degree)
