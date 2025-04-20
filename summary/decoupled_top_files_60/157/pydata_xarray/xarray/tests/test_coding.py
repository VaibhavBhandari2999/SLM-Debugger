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
    
    This function takes an xarray Variable that has been encoded using the CFMaskCoder and decodes it back to its original form, replacing the fill value with NaN.
    
    Parameters:
    original (xr.Variable): The encoded xarray Variable to be decoded.
    
    Returns:
    xr.Variable: The decoded xarray Variable with fill values replaced by NaN.
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
    original = xr.Variable(("x",), data, encoding=encoding)
    encoded = encode_cf_variable(original)

    assert encoded.dtype == encoded.attrs["missing_value"].dtype
    assert encoded.dtype == encoded.attrs["_FillValue"].dtype

    with pytest.warns(variables.SerializationWarning):
        roundtripped = decode_cf_variable("foo", encoded)
        assert_identical(roundtripped, original)


def test_CFMaskCoder_missing_value():
    """
    Tests the CFMaskCoder for handling missing values.
    
    This function tests the CFMaskCoder's ability to handle missing values in a dataset. It creates an expected DataArray with a specific missing value and then decodes and encodes it to check if the missing value is correctly preserved. If a different fill value is set in the decoded dataset's encoding, a ValueError is expected to be raised.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If a different fill value is set
    """

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
    original = xr.Variable(("x",), [0, -1, 1], {"_FillValue": -1}).chunk()
    expected = xr.Variable(("x",), [0, np.nan, 1])
    coder = variables.CFMaskCoder()
    encoded = coder.decode(original)
    assert isinstance(encoded.data, da.Array)
    assert_identical(expected, encoded)


# TODO(shoyer): port other fill-value tests


# TODO(shoyer): parameterize when we have more coders
def test_coder_roundtrip():
    original = xr.Variable(("x",), [0.0, np.nan, 1.0])
    coder = variables.CFMaskCoder()
    roundtripped = coder.decode(coder.encode(original))
    assert_identical(original, roundtripped)


@pytest.mark.parametrize("dtype", "u1 u2 i1 i2 f2 f4".split())
def test_scaling_converts_to_float32(dtype):
    """
    Tests that scaling an array converts it to float32.
    
    This function checks that when a variable with a specified data type is scaled,
    it is correctly converted to float32 during the encoding process. The round-trip
    process (encoding and then decoding) should preserve the original data, with the
    final result also being of type float32.
    
    Parameters:
    dtype (str): The data type of the original array.
    
    Returns:
    None: The function asserts that the original and round-tr
    """

    original = xr.Variable(
        ("x",), np.arange(10, dtype=dtype), encoding=dict(scale_factor=10)
    )
    coder = variables.CFScaleOffsetCoder()
    encoded = coder.encode(original)
    assert encoded.dtype == np.float32
    roundtripped = coder.decode(encoded)
    assert_identical(original, roundtripped)
    assert roundtripped.dtype == np.float32
