# Licensed under a 3-clause BSD style license - see LICENSE.rst

import functools

import numpy as np
import pytest

from astropy import units as u
from astropy.table import Table
from astropy.time import Time
from astropy.utils import iers
from astropy.utils.compat import PYTHON_LT_3_11
from astropy.utils.compat.optional_deps import HAS_H5PY

allclose_sec = functools.partial(
    np.allclose, rtol=2.0**-52, atol=2.0**-52 * 24 * 3600
)  # 20 ps atol
is_masked = np.ma.is_masked

# The first form is expanded to r"can't set attribute '{0}'" in Python 3.10, and replaced
# with the more informative second form as of 3.11 (python/cpython#31311).
no_setter_err = (
    r"can't set attribute"
    if PYTHON_LT_3_11
    else r"property '{0}' of '{1}' object has no setter"
)


def test_simple():
    """
    Test function for simple Time object operations.
    
    This function creates a Time object with a given format and checks if the initial mask is False and all elements are unmasked. It then tests the masking functionality by setting one element to masked and verifies that the mask is updated correctly. The function also checks if the format output remains an ndarray before masking and becomes a masked array after masking.
    
    Parameters:
    None
    
    Returns:
    None
    """

    t = Time([1, 2, 3], format="cxcsec")
    assert t.masked is False
    assert np.all(t.mask == [False, False, False])

    # Before masking, format output is not a masked array (it is an ndarray
    # like always)
    assert not isinstance(t.value, np.ma.MaskedArray)
    assert not isinstance(t.unix, np.ma.MaskedArray)

    t[2] = np.ma.masked
    assert t.masked is True
    assert np.all(t.mask == [False, False, True])
    assert allclose_sec(t.value[:2], [1, 2])
    assert is_masked(t.value[2])
    assert is_masked(t[2].value)

    # After masking format output is a masked array
    assert isinstance(t.value, np.ma.MaskedArray)
    assert isinstance(t.unix, np.ma.MaskedArray)
    # TODO : test all formats


def test_scalar_init():
    t = Time("2000:001")
    assert t.masked is False
    assert t.mask == np.array(False)


def test_mask_not_writeable():
    """
    Test that the 'mask' attribute of a Time object is not writable.
    
    This function checks if the 'mask' attribute of a Time object is read-only. It attempts to set the 'mask' attribute and raises an AttributeError if the attribute is not writable. It also checks if the 'mask' attribute of a list of Time objects is read-only and raises a ValueError if the attribute is writable.
    
    Parameters:
    None
    
    Returns:
    None
    """

    t = Time("2000:001")
    with pytest.raises(
        AttributeError, match=no_setter_err.format("mask", t.__class__.__name__)
    ):
        t.mask = True

    t = Time(["2000:001"])
    with pytest.raises(ValueError) as err:
        t.mask[0] = True
    assert "assignment destination is read-only" in str(err.value)


def test_str():
    """
    Generate a string representation of a Time object with masked values.
    
    This function creates a Time object with two date values and masks the second value. It then generates a string representation of the object and checks if the string matches the expected output. Additionally, it generates a representation of the ISO format of the Time object and checks if it matches the expected output. The function also demonstrates how to unmask and assign a new value to the masked entry.
    
    Parameters:
    - t: Time object with two date values.
    """

    t = Time(["2000:001", "2000:002"])
    t[1] = np.ma.masked
    assert str(t) == "['2000:001:00:00:00.000' --]"
    assert (
        repr(t)
        == "<Time object: scale='utc' format='yday' value=['2000:001:00:00:00.000' --]>"
    )

    expected = [
        "masked_array(data=['2000-01-01 00:00:00.000', --],",
        "             mask=[False,  True],",
        "       fill_value='N/A',",
        "            dtype='<U23')",
    ]

    # Note that we need to take care to allow for big-endian platforms,
    # for which the dtype will be >U23 instead of <U23, which we do with
    # the call to replace().
    assert repr(t.iso).replace(">U23", "<U23").splitlines() == expected

    # Assign value to unmask
    t[1] = "2000:111"
    assert str(t) == "['2000:001:00:00:00.000' '2000:111:00:00:00.000']"
    assert t.masked is False


def test_transform():
    """
    Transforms time objects between different scales and formats.
    
    This function takes a Time object with specified time values and transforms it to different time scales and formats. It also tests the handling of masked values during these transformations.
    
    Parameters:
    None (The function uses a Time object internally)
    
    Returns:
    None (The function modifies the Time object in place)
    
    Key Steps:
    1. Temporarily sets the auto_download configuration to False to prevent automatic downloading of IERS data.
    2. Creates a Time object with specified
    """

    with iers.conf.set_temp("auto_download", False):
        t = Time(["2000:001", "2000:002"])
        t[1] = np.ma.masked

        # Change scale (this tests the ERFA machinery with masking as well)
        t_ut1 = t.ut1
        assert is_masked(t_ut1.value[1])
        assert not is_masked(t_ut1.value[0])
        assert np.all(t_ut1.mask == [False, True])

        # Change format
        t_unix = t.unix
        assert is_masked(t_unix[1])
        assert not is_masked(t_unix[0])
        assert np.all(t_unix.mask == [False, True])


def test_masked_input():
    v0 = np.ma.MaskedArray([[1, 2], [3, 4]])  # No masked elements
    v1 = np.ma.MaskedArray([[1, 2], [3, 4]], mask=[[True, False], [False, False]])
    v2 = np.ma.MaskedArray([[10, 20], [30, 40]], mask=[[False, False], [False, True]])

    # Init from various combinations of masked arrays
    t = Time(v0, format="cxcsec")
    assert np.ma.allclose(t.value, v0)
    assert np.all(t.mask == [[False, False], [False, False]])
    assert t.masked is False

    t = Time(v1, format="cxcsec")
    assert np.ma.allclose(t.value, v1)
    assert np.all(t.mask == v1.mask)
    assert np.all(t.value.mask == v1.mask)
    assert t.masked is True

    t = Time(v1, v2, format="cxcsec")
    assert np.ma.allclose(t.value, v1 + v2)
    assert np.all(t.mask == (v1 + v2).mask)
    assert t.masked is True

    t = Time(v0, v1, format="cxcsec")
    assert np.ma.allclose(t.value, v0 + v1)
    assert np.all(t.mask == (v0 + v1).mask)
    assert t.masked is True

    t = Time(0, v2, format="cxcsec")
    assert np.ma.allclose(t.value, v2)
    assert np.all(t.mask == v2.mask)
    assert t.masked is True

    # Init from a string masked array
    t_iso = t.iso
    t2 = Time(t_iso)
    assert np.all(t2.value == t_iso)
    assert np.all(t2.mask == v2.mask)
    assert t2.masked is True


def test_all_masked_input():
    """Fix for #9612"""
    # Test with jd=0 and jd=np.nan. Both triggered an exception prior to #9624
    # due to astropy.utils.exceptions.ErfaError.
    for val in (0, np.nan):
        t = Time(np.ma.masked_array([val], mask=[True]), format="jd")
        assert str(t.iso) == "[--]"


def test_serialize_fits_masked(tmp_path):
    tm = Time([1, 2, 3], format="cxcsec")
    tm[1] = np.ma.masked

    fn = tmp_path / "tempfile.fits"
    t = Table([tm])
    t.write(fn)

    t2 = Table.read(fn, astropy_native=True)

    # Time FITS handling does not current round-trip format in FITS
    t2["col0"].format = tm.format

    assert t2["col0"].masked
    assert np.all(t2["col0"].mask == [False, True, False])
    assert np.all(t2["col0"].value == t["col0"].value)


@pytest.mark.skipif(not HAS_H5PY, reason="Needs h5py")
def test_serialize_hdf5_masked(tmp_path):
    tm = Time([1, 2, 3], format="cxcsec")
    tm[1] = np.ma.masked

    fn = tmp_path / "tempfile.hdf5"
    t = Table([tm])
    t.write(fn, path="root", serialize_meta=True)
    t2 = Table.read(fn)

    assert t2["col0"].masked
    assert np.all(t2["col0"].mask == [False, True, False])
    assert np.all(t2["col0"].value == t["col0"].value)


# Ignore warning in MIPS https://github.com/astropy/astropy/issues/9750
@pytest.mark.filterwarnings("ignore:invalid value encountered")
@pytest.mark.parametrize("serialize_method", ["jd1_jd2", "formatted_value"])
def test_serialize_ecsv_masked(serialize_method, tmp_path):
    tm = Time([1, 2, 3], format="cxcsec")
    tm[1] = np.ma.masked

    tm.info.serialize_method["ecsv"] = serialize_method

    fn = tmp_path / "tempfile.ecsv"
    t = Table([tm])
    t.write(fn)
    t2 = Table.read(fn)

    assert t2["col0"].masked
    assert np.all(t2["col0"].mask == [False, True, False])
    # Serializing formatted_value loses some precision.
    atol = 0.1 * u.us if serialize_method == "formatted_value" else 1 * u.ps
    assert np.all(abs(t2["col0"] - t["col0"]) <= atol)
