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
    Create and validate variable-length string or byte arrays.
    
    This function creates a NumPy dtype for variable-length strings or bytes,
    and validates its properties.
    
    Parameters:
    None
    
    Returns:
    None
    
    Tests:
    - Creates a vlen dtype with string elements and checks if the metadata
    contains the correct element type, whether it's a unicode dtype, and
    whether it's not a bytes dtype.
    - Creates a vlen dtype with bytes elements and checks if
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
    """
    Decodes an encoded string using the EncodedStringCoder.
    
    This function tests the decoding functionality of the EncodedStringCoder class. It initializes an instance of the class and uses it to decode a given array of encoded strings. The input is a `Variable` object containing the encoded data with a specified encoding attribute. The function decodes the data and compares the result with the expected output.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `strings.Enc
    """

    coder = strings.EncodedStringCoder()

    raw_data = np.array([b"abc", "ß∂µ∆".encode()])
    raw = Variable(("x",), raw_data, {"_Encoding": "utf-8"})
    actual = coder.decode(raw)

    expected = Variable(("x",), np.array(["abc", "ß∂µ∆"], dtype=object))
    assert_identical(actual, expected)

    assert_identical(coder.decode(actual[0]), expected[0])


@requires_dask
def test_EncodedStringCoder_decode_dask():
    """
    Decodes an encoded string using Dask.
    
    This function takes a Dask array of encoded strings and decodes them into a new Dask array of decoded strings. The decoding process is performed using the `EncodedStringCoder` class from the `strings` module.
    
    Parameters:
    None (The function uses predefined variables).
    
    Returns:
    None (The function asserts the correctness of the decoded output).
    
    Important Functions:
    - `EncodedStringCoder.decode`: Decodes the input Dask
    """

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
    Encodes string data using the specified coder.
    
    This function encodes string data into a format suitable for storage or transmission,
    ensuring compatibility with different character encodings. It supports both
    unicode and non-unicode strings based on the `allows_unicode` parameter.
    
    Parameters:
    raw (Variable): The input variable containing raw string data.
    
    Returns:
    Variable: The encoded variable with updated attributes.
    
    Examples:
    >>> raw_data = np.array(["abc", "ß∂µ
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
    """
    Test that the CharacterArrayCoder can round-trip an input string.
    
    Args:
    original (str): The original string to be encoded and decoded.
    
    Summary:
    This function tests the `CharacterArrayCoder` class by encoding and then decoding the input string `original`. It uses the `encode` and `decode` methods of the `CharacterArrayCoder` to ensure that the original and round-tripped strings are identical.
    """

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
    """
    Encodes a given dataset using the CharacterArrayCoder.
    
    This function takes a dataset `data` and encodes it using the
    CharacterArrayCoder. The encoded data is returned as a new dataset.
    
    Parameters:
    -----------
    data : array-like
    The input data to be encoded.
    
    Returns:
    --------
    encoded_data : xarray.Variable
    The encoded data with the original dimensions and an additional
    dimension 'string2' containing the encoded values.
    
    Example
    """

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
    """
    Encodes and decodes a string using CharacterArrayCoder, verifying the character dimension name.
    
    Args:
    original (str): The original string to be encoded.
    expected_char_dim_name (str): The expected character dimension name after encoding.
    
    Returns:
    None: This function does not return any value. It asserts that the encoded and decoded string maintains the expected character dimension name.
    
    Important Functions:
    - :meth:`strings.CharacterArrayCoder.encode`: Encodes the input string.
    """

    coder = strings.CharacterArrayCoder()
    encoded = coder.encode(original)
    roundtripped = coder.decode(encoded)
    assert encoded.dims[-1] == expected_char_dim_name
    assert roundtripped.encoding["char_dim_name"] == expected_char_dim_name
    assert roundtripped.dims[-1] == original.dims[-1]


def test_StackedBytesArray():
    """
    Summary: This function tests the StackedBytesArray class by creating an instance using a numpy array of bytes and comparing it to an expected result. It uses the StackedBytesArray class, numpy array, and assert_array_equal function.
    
    Parameters: None
    
    Returns: None
    
    Important Functions:
    - `numpy.array`: Creates a numpy array of bytes.
    - `strings.StackedBytesArray`: Initializes an instance of the StackedBytesArray class.
    - `assert_array_equal
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
    """
    Tests the behavior of the `StackedBytesArray` class when initialized with a scalar numpy array of bytes.
    
    This function creates a `StackedBytesArray` object from a numpy array containing byte strings and checks if its properties match those of the expected concatenated byte string. It also tests the behavior of the object when sliced using an `IndexerMaker` with a basic indexer.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the properties of the
    """

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
    """
    Index a StackedBytesArray using a vectorized indexer.
    
    This function tests indexing a `StackedBytesArray` object with a
    vectorized indexer created by `IndexerMaker`. The input is a 2D numpy
    array of bytes, converted into a `StackedBytesArray`. The indexer is
    generated to select specific elements from the array based on given indices,
    and the result is compared against an expected output.
    
    Parameters:
    None
    
    Returns:
    """

    array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]], dtype="S")
    stacked = strings.StackedBytesArray(array)
    expected = np.array([[b"abc", b"def"], [b"def", b"abc"]])

    V = IndexerMaker(indexing.VectorizedIndexer)
    indexer = V[np.array([[0, 1], [1, 0]])]
    actual = stacked[indexer]
    assert_array_equal(actual, expected)


def test_char_to_bytes():
    """
    Converts a 2D numpy array of bytes to a new 1D or 2D numpy array of concatenated bytes.
    
    Args:
    array (numpy.ndarray): A 2D numpy array where each element is a byte string.
    
    Returns:
    numpy.ndarray: A new 1D or 2D numpy array containing the concatenated byte strings from the input array.
    
    Examples:
    >>> import numpy as np
    >>> import strings
    >>> array = np.array([[b
    """

    array = np.array([[b"a", b"b", b"c"], [b"d", b"e", b"f"]])
    expected = np.array([b"abc", b"def"])
    actual = strings.char_to_bytes(array)
    assert_array_equal(actual, expected)

    expected = np.array([b"ad", b"be", b"cf"])
    actual = strings.char_to_bytes(array.T)  # non-contiguous
    assert_array_equal(actual, expected)


def test_char_to_bytes_ndim_zero():
    """
    Converts a single character to its byte representation.
    
    This function takes a NumPy array containing a single character and
    converts it into a byte representation using the `strings.char_to_bytes`
    function.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> expected = np.array(b'a')
    >>> actual = strings.char_to_bytes(expected)
    >>> assert_array_equal(actual, expected)
    """

    expected = np.array(b"a")
    actual = strings.char_to_bytes(expected)
    assert_array_equal(actual, expected)


def test_char_to_bytes_size_zero():
    """
    Converts an array of zero-sized byte strings to a NumPy array of bytes.
    
    This function takes an input array with a shape of (3, 0) and data type 'S1',
    representing an array of zero-sized byte strings, and converts it into a NumPy
    array of bytes. The resulting array contains three elements, each being an
    empty byte string.
    
    Parameters:
    array (numpy.ndarray): Input array with shape (3, 0) and
    """

    array = np.zeros((3, 0), dtype="S1")
    expected = np.array([b"", b"", b""])
    actual = strings.char_to_bytes(array)
    assert_array_equal(actual, expected)


@requires_dask
def test_char_to_bytes_dask():
    """
    Converts a Dask array of bytes to a single Dask array of concatenated bytes.
    
    This function takes a Dask array containing byte strings and converts it into a single Dask array where the byte strings are concatenated along the first axis. The resulting array has a chunk size of 2 along the first dimension and a dtype of 'S3'.
    
    Parameters:
    array (da.Array): A Dask array of shape (2, 3) containing byte strings.
    
    Returns:
    """

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
    """
    Converts an array of bytes to an array of characters.
    
    This function takes an input array of bytes and converts each byte into its corresponding character representation. It supports both contiguous and non-contiguous arrays.
    
    Parameters:
    array (numpy.ndarray): Input array containing bytes.
    
    Returns:
    numpy.ndarray: Array where each byte is converted to its corresponding character.
    
    Examples:
    >>> import numpy as np
    >>> from your_module import bytes_to_char
    
    >>> array = np.array([[
    """

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
    Converts a Dask array of bytes to a Dask array of characters.
    
    Args:
    array (dask.array.Array): A Dask array containing byte sequences.
    
    Returns:
    dask.array.Array: A Dask array where each byte sequence is split into individual characters.
    
    Example:
    >>> numpy_array = np.array([b'ab', b'cd'])
    >>> array = da.from_array(numpy_array, ((1, 1),))
    >>> result = bytes_to
    """

    numpy_array = np.array([b"ab", b"cd"])
    array = da.from_array(numpy_array, ((1, 1),))
    expected = np.array([[b"a", b"b"], [b"c", b"d"]])
    actual = strings.bytes_to_char(array)
    assert isinstance(actual, da.Array)
    assert actual.chunks == ((1, 1), ((2,)))
    assert actual.dtype == "S1"
    assert_array_equal(np.array(actual), expected)
