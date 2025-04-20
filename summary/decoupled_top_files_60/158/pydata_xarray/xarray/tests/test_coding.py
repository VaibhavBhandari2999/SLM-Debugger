from contextlib import suppress

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.coding import variables
from xarray.conventions import decode_cf_variable, encode_cf_variable

from . import assert_equal, assert_identical, requires_dask

with suppress(ImportError):
    import dask.array as da


def test_CFMaskCoder_decode():
    """
    Decode a CFMaskCoder encoded variable.
    
    This function takes an xarray Variable that has been encoded using a CFMaskCoder
    and decodes it back to its original form, replacing the fill value with NaN.
    
    Parameters:
    original (xarray.Variable): The encoded variable to be decoded.
    
    Returns:
    xarray.Variable: The decoded variable with fill values replaced by NaN.
    """

    original = xr.Variable(("x",), [0, -1, 1], {"_FillValue": -1})
    expected = xr.Variable(("x",), [0, np.nan, 1])
    coder = variables.CFMaskCoder()
    encoded = coder.decode(original)
    assert_identical(expected, encoded)


encoding_with_dtype = {
    "dtype": np.dtype("float64"),
    "_FillValue": np.float32(1e20),
    "missing_value": np.float64(1e20),
}
encoding_without_dtype = {
    "_FillValue": np.float32(1e20),
    "missing_value": np.float64(1e20),
}
CFMASKCODER_ENCODE_DTYPE_CONFLICT_TESTS = {
    "numeric-with-dtype": ([0.0, -1.0, 1.0], encoding_with_dtype),
    "numeric-without-dtype": ([0.0, -1.0, 1.0], encoding_without_dtype),
    "times-with-dtype": (pd.date_range("2000", periods=3), encoding_with_dtype),
}


@pytest.mark.parametrize(
    ("data", "encoding"),
    CFMASKCODER_ENCODE_DTYPE_CONFLICT_TESTS.values(),
    ids=list(CFMASKCODER_ENCODE_DTYPE_CONFLICT_TESTS.keys()),
)
def test_CFMaskCoder_encode_missing_fill_values_conflict(data, encoding):
    """
    Encode a CF variable with missing values and fill values.
    
    This function takes an xarray Variable and its encoding, encodes the variable
    according to the CF conventions, and ensures that the missing value and fill
    value are consistent. If there is a conflict between the missing value and
    fill value, a warning is issued.
    
    Parameters:
    data (xarray.Variable): The input data variable to be encoded.
    encoding (dict): The encoding attributes for the variable.
    
    Returns:
    xarray.Variable
    """

    original = xr.Variable(("x",), data, encoding=encoding)
    encoded = encode_cf_variable(original)

    assert encoded.dtype == encoded.attrs["missing_value"].dtype
    assert encoded.dtype == encoded.attrs["_FillValue"].dtype

    with pytest.warns(variables.SerializationWarning):
        roundtripped = decode_cf_variable("foo", encoded)
        assert_identical(roundtripped, original)


def test_CFMaskCoder_missing_value():
    expected = xr.DataArray(
        np.array([[26915, 27755, -9999, 27705], [25595, -9999, 28315, -9999]]),
        dims=["npts", "ntimes"],
        name="tmpk",
    )
    expected.attrs["missing_value"] = -9999

    decoded = xr.decode_cf(expected.to_dataset())
    encoded, _ = xr.conventions.cf_encoder(decoded, decoded.attrs)

    assert_equal(encoded["tmpk"], expected.variable)

    decoded.tmpk.encoding["_FillValue"] = -9940
    with pytest.raises(ValueError):
        encoded, _ = xr.conventions.cf_encoder(decoded, decoded.attrs)


@requires_dask
def test_CFMaskCoder_decode_dask():
    """
    Decode a dask array using the CFMaskCoder.
    
    This function takes a dask array with a '_FillValue' attribute and decodes it using the CFMaskCoder. The result is a dask array with NaN values where the original array had the fill value.
    
    Parameters:
    original (xr.Variable): A dask array with the '_FillValue' attribute.
    
    Returns:
    xr.Variable: A dask array with the fill values replaced by NaNs.
    """

    original = xr.Variable(("x",), [0, -1, 1], {"_FillValue": -1}).chunk()
    expected = xr.Variable(("x",), [0, np.nan, 1])
    coder = variables.CFMaskCoder()
    encoded = coder.decode(original)
    assert isinstance(encoded.data, da.Array)
    assert_identical(expected, encoded)


# TODO(shoyer): port other fill-value tests


# TODO(shoyer): parameterize when we have more coders
def test_coder_roundtrip():
    """
    Test that a variable can be encoded and decoded using the CFMaskCoder without losing information.
    
    Parameters:
    original (xr.Variable): An xarray Variable with a dimension 'x' and values [0.0, np.nan, 1.0].
    
    Returns:
    None: The function asserts that the original and roundtripped variables are identical.
    """

    original = xr.Variable(("x",), [0.0, np.nan, 1.0])
    coder = variables.CFMaskCoder()
    roundtripped = coder.decode(coder.encode(original))
    assert_identical(original, roundtripped)


@pytest.mark.parametrize("dtype", "u1 u2 i1 i2 f2 f4".split())
def test_scaling_converts_to_float32(dtype):
    original = xr.Variable(
        ("x",), np.arange(10, dtype=dtype), encoding=dict(scale_factor=10)
    )
    coder = variables.CFScaleOffsetCoder()
    encoded = coder.encode(original)
    assert encoded.dtype == np.float32
    roundtripped = coder.decode(encoded)
    assert_identical(original, roundtripped)
    assert roundtripped.dtype == np.float32
