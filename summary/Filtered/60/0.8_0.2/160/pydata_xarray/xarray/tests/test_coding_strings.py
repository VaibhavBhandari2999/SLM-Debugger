from contextlib import suppress

import numpy as np
import pytest

from xarray import Variable
from xarray.coding import strings
from xarray.core import indexing

from . import (
    IndexerMaker,
    assert_array_equal,
    assert_identical,
    raises_regex,
    requires_dask,
)

with suppress(ImportError):
    import dask.array as da


def test_vlen_dtype():
    """
    Test the creation and validation of variable-length string and bytes data types.
    
    This function checks the creation of variable-length string and bytes data types using the `create_vlen_dtype` function and validates them using the `is_unicode_dtype`, `is_bytes_dtype`, and `check_vlen_dtype` functions.
    
    Parameters:
    None
    
    Returns:
    None
    """

    dtype = strings.create_vlen_dtype(str)
    assert dtype.metadata["element_type"] == str
    assert strings.is_unicode_dtype(dtype)
    assert not strings.is_bytes_dtype(dtype)
    assert strings.check_vlen_dtype(dtype) is str

    dtype = strings.create_vlen_dtype(bytes)
    assert dtype.metadata["element_type"] == bytes
    assert not strings.is_unicode_dtype(dtype)
    assert strings.is_bytes_dtype(dtype)
    assert strings.check_vlen_dtype(dtype) is bytes

    assert strings.check_vlen_dtype(np.dtype(object)) is None


def test_EncodedStringCoder_decode():
    coder = strings.EncodedStringCoder()

    raw_data = np.array([b"abc", "ß∂µ∆".encode()])
    raw = Variable(("x",), raw_data, {"_Encoding": "utf-8"})
    actual = coder.decode(raw)

    expected = Variable(("x",), np.array(["abc", "ß∂µ∆"], dtype=object))
    assert_identical(actual, expected)

    assert_identical(coder.decode(actual[0]), expected[0])


@requires_dask
def test_EncodedStringCoder_decode_dask():
    coder = strings.EncodedStringCoder()

    raw_data = np.array([b"abc", "ß∂µ∆".encode()])
    raw = Variable(("x",), raw_data, {"_Encoding": "utf-8"}).chunk()
    actual = coder.decode(raw)
    assert isinstance(actual.data, da.Array)

    expected = Variable(("x",), np.array(["abc", "ß∂µ∆"], dtype=object))
    assert_identical(actual, expected)

    actual_indexed = coder.decode(actual[0])
    assert isinstance(actual_indexed.data, da.Array)
    assert_identical(actual_indexed, expected[0])


def test_EncodedStringCoder_encode():
    """
    Encodes a VlenString variable using the specified encoding.
    
    This function encodes a VlenString variable into a byte string format. It supports both unicode and non-unicode strings.
    
    Parameters:
    raw (Variable): The input VlenString variable to be encoded.
    
    Keyword Arguments:
    allows_unicode (bool): If True, the function will allow unicode strings in the input. Default is True.
    
    Returns:
    Variable: The encoded variable with the appropriate encoding applied.
    """

    dtype = strings.create_vlen_dtype(str)
    raw_data = np.array(["abc", "ß∂µ∆"], dtype=dtype)
    expected_data = np.array([r.encode("utf-8") for r in raw_data], dtype=object)

    coder = strings.EncodedStringCoder(allows_unicode=True)
    raw = Variable(("x",), raw_data, encoding={"dtype": "S1"})
    actual = coder.encode(raw)
    expected = Variable(("x",), expected_data, attrs={"_Encoding": "utf-8"})
    assert_identical(actual, expected)

    raw = Variable(("x",), raw_data)
    assert_identical(coder.encode(raw), raw)

    coder = strings.EncodedStringCoder(allows_unicode=False)
    assert_identical(coder.encode(raw), expected)


@pytest.mark.parametrize(
    "original",
    [
        Variable(("x",), [b"ab", b"cdef"]),
        Variable((), b"ab"),
        Variable(("x",), [b"a", b"b"]),
        Variable((), b"a"),
    ],
)
def test_CharacterArrayCoder_roundtrip(original):
    coder = strings.CharacterArrayCoder()
    roundtripped = coder.decode(coder.encode(original))
    assert_identical(original, roundtripped)


@pytest.mark.parametrize(
    "data",
    [
        np.array([b"a", b"bc"]),
        np.array([b"a", b"bc"], dtype=strings.create_vlen_dtype(bytes)),
    ],
)
def test_CharacterArrayCoder_encode(data):
    coder = strings.CharacterArrayCoder()
    raw = Variable(("x",), data)
    actual = coder.encode(raw)
    expected = Variable(("x", "string2"), np.array([[b"a", b""], [b"b", b"c"]]))
    assert_identical(actual, expected)


@pytest.mark.parametrize(
    ["original", "expected_char_dim_name"],
    [
        (Variable(("x",), [b"ab", b"cdef"]), "string4"),
        (Variable(("x",), [b"ab", b"cdef"], encoding={"char_dim_name": "foo"}), "foo"),
    ],
)
def test_CharacterArrayCoder_char_dim_name(original, expected_char_dim_name):
    coder = strings.CharacterArrayCoder()
    encoded = coder.encode(original)
    roundtripped = coder.decode(encoded)
    assert encoded.dims[-1] == expected_char_dim_name
    assert roundtripped.encoding["char_dim_name"] == expected_char_dim_name
    assert roundtripped.dims[-1] == original.dims[-1]


def test_StackedBytesArray():
    """
    Tests the StackedBytesArray function.
    
    This function checks the behavior of the StackedBytesArray function by comparing the output with an expected result. The function takes a numpy array of bytes as input and returns a new array where the bytes are stacked together.
    
    Parameters:
    array (numpy.ndarray): A numpy array of bytes with shape (n, m).
    
    Returns:
    numpy.ndarray: A new numpy array of bytes where each row is a single byte string formed by concatenating the bytes in the corresponding rows of
    """

    array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]], dtype="S")
    actual = strings.StackedBytesArray(array)
    expected = np.array([b"abc", b"def"], dtype="S")
    assert actual.dtype == expected.dtype
    assert actual.shape == expected.shape
    assert actual.size == expected.size
    assert actual.ndim == expected.ndim
    assert len(actual) == len(expected)
    assert_array_equal(expected, actual)

    B = IndexerMaker(indexing.BasicIndexer)
    assert_array_equal(expected[:1], actual[B[:1]])
    with pytest.raises(IndexError):
        actual[B[:, :2]]


def test_StackedBytesArray_scalar():
    array = np.array([b"a", b"b", b"c"], dtype="S")
    actual = strings.StackedBytesArray(array)

    expected = np.array(b"abc")
    assert actual.dtype == expected.dtype
    assert actual.shape == expected.shape
    assert actual.size == expected.size
    assert actual.ndim == expected.ndim
    with pytest.raises(TypeError):
        len(actual)
    np.testing.assert_array_equal(expected, actual)

    B = IndexerMaker(indexing.BasicIndexer)
    with pytest.raises(IndexError):
        actual[B[:2]]


def test_StackedBytesArray_vectorized_indexing():
    array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]], dtype="S")
    stacked = strings.StackedBytesArray(array)
    expected = np.array([[b"abc", b"def"], [b"def", b"abc"]])

    V = IndexerMaker(indexing.VectorizedIndexer)
    indexer = V[np.array([[0, 1], [1, 0]])]
    actual = stacked[indexer]
    assert_array_equal(actual, expected)


def test_char_to_bytes():
    array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]])
    expected = np.array([b"abc", b"def"])
    actual = strings.char_to_bytes(array)
    assert_array_equal(actual, expected)

    expected = np.array([b"ad", b"be", b"cf"])
    actual = strings.char_to_bytes(array.T)  # non-contiguous
    assert_array_equal(actual, expected)


def test_char_to_bytes_ndim_zero():
    expected = np.array(b"a")
    actual = strings.char_to_bytes(expected)
    assert_array_equal(actual, expected)


def test_char_to_bytes_size_zero():
    array = np.zeros((3, 0), dtype="S1")
    expected = np.array([b"", b"", b""])
    actual = strings.char_to_bytes(array)
    assert_array_equal(actual, expected)


@requires_dask
def test_char_to_bytes_dask():
    numpy_array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]])
    array = da.from_array(numpy_array, ((2,), (3,)))
    expected = np.array([b"abc", b"def"])
    actual = strings.char_to_bytes(array)
    assert isinstance(actual, da.Array)
    assert actual.chunks == ((2,),)
    assert actual.dtype == "S3"
    assert_array_equal(np.array(actual), expected)

    with raises_regex(ValueError, "stacked dask character array"):
        strings.char_to_bytes(array.rechunk(1))


def test_bytes_to_char():
    array = np.array([[b"ab", b"cd"], [b"ef", b"gh"]])
    expected = np.array([[[b"a", b"b"], [b"c", b"d"]], [[b"e", b"f"], [b"g", b"h"]]])
    actual = strings.bytes_to_char(array)
    assert_array_equal(actual, expected)

    expected = np.array([[[b"a", b"b"], [b"e", b"f"]], [[b"c", b"d"], [b"g", b"h"]]])
    actual = strings.bytes_to_char(array.T)  # non-contiguous
    assert_array_equal(actual, expected)


@requires_dask
def test_bytes_to_char_dask():
    """
    Convert a Dask array of bytes to a Dask array of characters.
    
    Parameters:
    array (da.Array): A Dask array of bytes.
    
    Returns:
    da.Array: A Dask array of characters.
    
    Example:
    >>> numpy_array = np.array([b"ab", b"cd"])
    >>> array = da.from_array(numpy_array, ((1, 1),))
    >>> actual = strings.bytes_to_char(array)
    >>> actual.chunks
    ((1, 1
    """

    numpy_array = np.array([b"ab", b"cd"])
    array = da.from_array(numpy_array, ((1, 1),))
    expected = np.array([[b"a", b"b"], [b"c", b"d"]])
    actual = strings.bytes_to_char(array)
    assert isinstance(actual, da.Array)
    assert actual.chunks == ((1, 1), ((2,)))
    assert actual.dtype == "S1"
    assert_array_equal(np.array(actual), expected)
al, da.Array)
    assert actual.chunks == ((1, 1), ((2,)))
    assert actual.dtype == "S1"
    assert_array_equal(np.array(actual), expected)
