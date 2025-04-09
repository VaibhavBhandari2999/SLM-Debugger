import sys
from textwrap import dedent

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.core import formatting

from . import raises_regex


class TestFormatting:
    def test_get_indexer_at_least_n_items(self):
        """
        Tests the `_get_indexer_at_least_n_items` function for generating indexers that ensure at least a specified number of items are selected.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `_get_indexer_at_least_n_items` function with various input shapes and checks if the generated indexers match the expected results. The function uses slices to define the indexers and ensures that at least 10 items are selected from the given shapes. It
        """

        cases = [
            ((20,), (slice(10),), (slice(-10, None),)),
            ((3, 20), (0, slice(10)), (-1, slice(-10, None))),
            ((2, 10), (0, slice(10)), (-1, slice(-10, None))),
            ((2, 5), (slice(2), slice(None)), (slice(-2, None), slice(None))),
            ((1, 2, 5), (0, slice(2), slice(None)), (-1, slice(-2, None), slice(None))),
            ((2, 3, 5), (0, slice(2), slice(None)), (-1, slice(-2, None), slice(None))),
            (
                (1, 10, 1),
                (0, slice(10), slice(None)),
                (-1, slice(-10, None), slice(None)),
            ),
            (
                (2, 5, 1),
                (slice(2), slice(None), slice(None)),
                (slice(-2, None), slice(None), slice(None)),
            ),
            ((2, 5, 3), (0, slice(4), slice(None)), (-1, slice(-4, None), slice(None))),
            (
                (2, 3, 3),
                (slice(2), slice(None), slice(None)),
                (slice(-2, None), slice(None), slice(None)),
            ),
        ]
        for shape, start_expected, end_expected in cases:
            actual = formatting._get_indexer_at_least_n_items(shape, 10, from_end=False)
            assert start_expected == actual
            actual = formatting._get_indexer_at_least_n_items(shape, 10, from_end=True)
            assert end_expected == actual

    def test_first_n_items(self):
        """
        Tests the `first_n_items` function from the `formatting` module.
        
        This function checks if the `first_n_items` function correctly returns the first `n` items of a reshaped NumPy array. It also verifies that an error is raised when `n` is less than or equal to zero.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `first_n_items`: The function under test from the `formatting` module.
        """

        array = np.arange(100).reshape(10, 5, 2)
        for n in [3, 10, 13, 100, 200]:
            actual = formatting.first_n_items(array, n)
            expected = array.flat[:n]
            assert (expected == actual).all()

        with raises_regex(ValueError, "at least one item"):
            formatting.first_n_items(array, 0)

    def test_last_n_items(self):
        """
        Tests the `last_n_items` function from the `formatting` module.
        
        This function verifies that the `last_n_items` function correctly extracts
        the last `n` items from a flattened NumPy array. It also checks that an error
        is raised when attempting to extract zero or fewer items.
        
        Parameters:
        - array: A NumPy array from which to extract the last `n` items.
        - n: The number of items to extract from the end of
        """

        array = np.arange(100).reshape(10, 5, 2)
        for n in [3, 10, 13, 100, 200]:
            actual = formatting.last_n_items(array, n)
            expected = array.flat[-n:]
            assert (expected == actual).all()

        with raises_regex(ValueError, "at least one item"):
            formatting.first_n_items(array, 0)

    def test_last_item(self):
        """
        Tests the `last_item` function by reshaping an array of integers from 0 to 99 and verifying that the last item is correctly extracted for different reshape configurations.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `np.arange`: Generates an array of integers from 0 to 99.
        - `array.reshape`: Reshapes the generated array into specified configurations.
        - `formatting.last_item`: Extracts the last item from
        """

        array = np.arange(100)

        reshape = ((10, 10), (1, 100), (2, 2, 5, 5))
        expected = np.array([99])

        for r in reshape:
            result = formatting.last_item(array.reshape(r))
            assert result == expected

    def test_format_item(self):
        """
        Format various types of input items into a standardized string representation.
        
        This function takes different types of input items such as timestamps, timedeltas,
        strings, bytes, numbers, and NaN values, and formats them into a standardized string
        representation. The function handles `pd.Timestamp`, `pd.Timedelta`, and `pd.NaT`
        specifically, converting them to their respective string formats. For other types like
        strings, bytes, and numeric values, it wraps them in quotes
        """

        cases = [
            (pd.Timestamp("2000-01-01T12"), "2000-01-01T12:00:00"),
            (pd.Timestamp("2000-01-01"), "2000-01-01"),
            (pd.Timestamp("NaT"), "NaT"),
            (pd.Timedelta("10 days 1 hour"), "10 days 01:00:00"),
            (pd.Timedelta("-3 days"), "-3 days +00:00:00"),
            (pd.Timedelta("3 hours"), "0 days 03:00:00"),
            (pd.Timedelta("NaT"), "NaT"),
            ("foo", "'foo'"),
            (b"foo", "b'foo'"),
            (1, "1"),
            (1.0, "1.0"),
            (np.float16(1.1234), "1.123"),
            (np.float32(1.0111111), "1.011"),
            (np.float64(22.222222), "22.22"),
        ]
        for item, expected in cases:
            actual = formatting.format_item(item)
            assert expected == actual

    def test_format_items(self):
        """
        Format a list of items into a string representation.
        
        This function takes a list of items, which can be either NumPy timedelta64
        objects or pandas Timedelta objects, and formats them into a space-separated
        string. The function handles different units of time and special cases like
        'NaT' (Not a Time).
        
        Parameters:
        None
        
        Returns:
        None
        
        Examples:
        - For an array of NumPy timedelta64 objects with unit '
        """

        cases = [
            (np.arange(4) * np.timedelta64(1, "D"), "0 days 1 days 2 days 3 days"),
            (
                np.arange(4) * np.timedelta64(3, "h"),
                "00:00:00 03:00:00 06:00:00 09:00:00",
            ),
            (
                np.arange(4) * np.timedelta64(500, "ms"),
                "00:00:00 00:00:00.500000 00:00:01 00:00:01.500000",
            ),
            (pd.to_timedelta(["NaT", "0s", "1s", "NaT"]), "NaT 00:00:00 00:00:01 NaT"),
            (
                pd.to_timedelta(["1 day 1 hour", "1 day", "0 hours"]),
                "1 days 01:00:00 1 days 00:00:00 0 days 00:00:00",
            ),
            ([1, 2, 3], "1 2 3"),
        ]
        for item, expected in cases:
            actual = " ".join(formatting.format_items(item))
            assert expected == actual

    def test_format_array_flat(self):
        """
        Format a NumPy array into a flat string representation.
        
        This function formats a given NumPy array into a flat string representation, with optional truncation based on the specified number of elements to display. The function handles both integer and floating-point arrays, and includes special handling for very long strings.
        
        Parameters:
        - arr (np.ndarray): The input NumPy array to be formatted.
        - num_elements (int): The number of elements to display before and after the ellipsis ('...')
        """

        actual = formatting.format_array_flat(np.arange(100), 2)
        expected = "..."
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(100), 9)
        expected = "0 ... 99"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(100), 10)
        expected = "0 1 ... 99"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(100), 13)
        expected = "0 1 ... 98 99"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(100), 15)
        expected = "0 1 2 ... 98 99"
        assert expected == actual

        # NB: Probably not ideal; an alternative would be cutting after the
        # first ellipsis
        actual = formatting.format_array_flat(np.arange(100.0), 11)
        expected = "0.0 ... ..."
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(100.0), 12)
        expected = "0.0 ... 99.0"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(3), 5)
        expected = "0 1 2"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(4.0), 11)
        expected = "0.0 ... 3.0"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(0), 0)
        expected = ""
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(1), 1)
        expected = "0"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(2), 3)
        expected = "0 1"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(4), 7)
        expected = "0 1 2 3"
        assert expected == actual

        actual = formatting.format_array_flat(np.arange(5), 7)
        expected = "0 ... 4"
        assert expected == actual

        long_str = [" ".join(["hello world" for _ in range(100)])]
        actual = formatting.format_array_flat(np.asarray([long_str]), 21)
        expected = "'hello world hello..."
        assert expected == actual

    def test_pretty_print(self):
        assert formatting.pretty_print("abcdefghij", 8) == "abcde..."
        assert formatting.pretty_print("ß", 1) == "ß"

    def test_maybe_truncate(self):
        assert formatting.maybe_truncate("ß", 10) == "ß"

    def test_format_timestamp_out_of_bounds(self):
        """
        Tests the `format_timestamp` function for handling dates outside the typical range.
        
        This function checks if the `format_timestamp` function correctly formats dates that are out of the standard range (1300-2300). It uses the `datetime` module to create test dates and compares the formatted output with the expected results.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `datetime`: Used to create test date objects.
        - `format
        """

        from datetime import datetime

        date = datetime(1300, 12, 1)
        expected = "1300-12-01"
        result = formatting.format_timestamp(date)
        assert result == expected

        date = datetime(2300, 12, 1)
        expected = "2300-12-01"
        result = formatting.format_timestamp(date)
        assert result == expected

    def test_attribute_repr(self):
        """
        Tests the `summarize_attr` function from the `formatting` module.
        
        This function checks that the `summarize_attr` function correctly handles different types of input strings, including short strings, very long strings, strings with newlines, and strings with tabs. It ensures that the output is properly formatted and truncated as necessary.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the assertions fail.
        
        Important Functions:
        -
        """

        short = formatting.summarize_attr("key", "Short string")
        long = formatting.summarize_attr("key", 100 * "Very long string ")
        newlines = formatting.summarize_attr("key", "\n\n\n")
        tabs = formatting.summarize_attr("key", "\t\t\t")
        assert short == "    key: Short string"
        assert len(long) <= 80
        assert long.endswith("...")
        assert "\n" not in newlines
        assert "\t" not in tabs

    def test_diff_array_repr(self):
        """
        \
        Left and right DataArray objects are not identical
        Differing dimensions:
        (x: 2, y: 3) != (x: 2)
        Differing values:
        L
        array([[1, 2, 3],
        [4, 5, 6]], dtype=int64)
        R
        array([1, 2], dtype=int64)
        Differing coordinates:
        L * x        (x) %cU1 'a' 'b'
        R * x        (x) %cU1 'a' 'c'
        Coordinates only on the left object:
        * y        (y) int64 1 2 3
        Coordinates only on the right object:
        label    (x) int64 1 2
        Differing attributes:
        L   units: m
        R   units: kg
        Attributes only on the left object:
        description: desc
        """

        da_a = xr.DataArray(
            np.array([[1, 2, 3], [4, 5, 6]], dtype="int64"),
            dims=("x", "y"),
            coords={
                "x": np.array(["a", "b"], dtype="U1"),
                "y": np.array([1, 2, 3], dtype="int64"),
            },
            attrs={"units": "m", "description": "desc"},
        )

        da_b = xr.DataArray(
            np.array([1, 2], dtype="int64"),
            dims="x",
            coords={
                "x": np.array(["a", "c"], dtype="U1"),
                "label": ("x", np.array([1, 2], dtype="int64")),
            },
            attrs={"units": "kg"},
        )

        byteorder = "<" if sys.byteorder == "little" else ">"
        expected = dedent(
            """\
        Left and right DataArray objects are not identical
        Differing dimensions:
            (x: 2, y: 3) != (x: 2)
        Differing values:
        L
            array([[1, 2, 3],
                   [4, 5, 6]], dtype=int64)
        R
            array([1, 2], dtype=int64)
        Differing coordinates:
        L * x        (x) %cU1 'a' 'b'
        R * x        (x) %cU1 'a' 'c'
        Coordinates only on the left object:
          * y        (y) int64 1 2 3
        Coordinates only on the right object:
            label    (x) int64 1 2
        Differing attributes:
        L   units: m
        R   units: kg
        Attributes only on the left object:
            description: desc"""
            % (byteorder, byteorder)
        )

        actual = formatting.diff_array_repr(da_a, da_b, "identical")
        try:
            assert actual == expected
        except AssertionError:
            # depending on platform, dtype may not be shown in numpy array repr
            assert actual == expected.replace(", dtype=int64", "")

        va = xr.Variable(
            "x", np.array([1, 2, 3], dtype="int64"), {"title": "test Variable"}
        )
        vb = xr.Variable(("x", "y"), np.array([[1, 2, 3], [4, 5, 6]], dtype="int64"))

        expected = dedent(
            """\
        Left and right Variable objects are not equal
        Differing dimensions:
            (x: 3) != (x: 2, y: 3)
        Differing values:
        L
            array([1, 2, 3], dtype=int64)
        R
            array([[1, 2, 3],
                   [4, 5, 6]], dtype=int64)"""
        )

        actual = formatting.diff_array_repr(va, vb, "equals")
        try:
            assert actual == expected
        except AssertionError:
            assert actual == expected.replace(", dtype=int64", "")

    @pytest.mark.filterwarnings("error")
    def test_diff_attrs_repr_with_array(self):
        """
        \
        Differing attributes:
        L   attr: [0 1]
        R   attr: 1
        """

        attrs_a = {"attr": np.array([0, 1])}

        attrs_b = {"attr": 1}
        expected = dedent(
            """\
            Differing attributes:
            L   attr: [0 1]
            R   attr: 1
            """
        ).strip()
        actual = formatting.diff_attrs_repr(attrs_a, attrs_b, "equals")
        assert expected == actual

        attrs_b = {"attr": np.array([-3, 5])}
        expected = dedent(
            """\
            Differing attributes:
            L   attr: [0 1]
            R   attr: [-3  5]
            """
        ).strip()
        actual = formatting.diff_attrs_repr(attrs_a, attrs_b, "equals")
        assert expected == actual

        # should not raise a warning
        attrs_b = {"attr": np.array([0, 1, 2])}
        expected = dedent(
            """\
            Differing attributes:
            L   attr: [0 1]
            R   attr: [0 1 2]
            """
        ).strip()
        actual = formatting.diff_attrs_repr(attrs_a, attrs_b, "equals")
        assert expected == actual

    def test_diff_dataset_repr(self):
        """
        \
        Left and right Dataset objects are not identical
        Differing dimensions:
        (x: 2, y: 3) != (x: 2)
        Differing coordinates:
        L * x        (x) %cU1 'a' 'b'
        R * x        (x) %cU1 'a' 'c'
        source: 0
        Coordinates only on the left object:
        * y        (y) int64 1 2 3
        Coordinates only on the right object:
        label    (x) int64 1 2
        Differing data variables:
        L   var1     (x, y) int64 1 2 3 4 5 6
        R   var1     (x) int64 1 2
        Data variables only on the left object:
        var2     (x) int64 3 4
        Differing attributes:
        L   units: m
        R   units: kg
        Attributes only on the left object:
        description: desc
        """

        ds_a = xr.Dataset(
            data_vars={
                "var1": (("x", "y"), np.array([[1, 2, 3], [4, 5, 6]], dtype="int64")),
                "var2": ("x", np.array([3, 4], dtype="int64")),
            },
            coords={
                "x": np.array(["a", "b"], dtype="U1"),
                "y": np.array([1, 2, 3], dtype="int64"),
            },
            attrs={"units": "m", "description": "desc"},
        )

        ds_b = xr.Dataset(
            data_vars={"var1": ("x", np.array([1, 2], dtype="int64"))},
            coords={
                "x": ("x", np.array(["a", "c"], dtype="U1"), {"source": 0}),
                "label": ("x", np.array([1, 2], dtype="int64")),
            },
            attrs={"units": "kg"},
        )

        byteorder = "<" if sys.byteorder == "little" else ">"
        expected = dedent(
            """\
        Left and right Dataset objects are not identical
        Differing dimensions:
            (x: 2, y: 3) != (x: 2)
        Differing coordinates:
        L * x        (x) %cU1 'a' 'b'
        R * x        (x) %cU1 'a' 'c'
            source: 0
        Coordinates only on the left object:
          * y        (y) int64 1 2 3
        Coordinates only on the right object:
            label    (x) int64 1 2
        Differing data variables:
        L   var1     (x, y) int64 1 2 3 4 5 6
        R   var1     (x) int64 1 2
        Data variables only on the left object:
            var2     (x) int64 3 4
        Differing attributes:
        L   units: m
        R   units: kg
        Attributes only on the left object:
            description: desc"""
            % (byteorder, byteorder)
        )

        actual = formatting.diff_dataset_repr(ds_a, ds_b, "identical")
        assert actual == expected

    def test_array_repr(self):
        """
        \
        <xarray.DataArray (1, 2) (test: 1)>
        array([0])
        Dimensions without coordinates: test
        """

        ds = xr.Dataset(coords={"foo": [1, 2, 3], "bar": [1, 2, 3]})
        ds[(1, 2)] = xr.DataArray([0], dims="test")
        actual = formatting.array_repr(ds[(1, 2)])
        expected = dedent(
            """\
        <xarray.DataArray (1, 2) (test: 1)>
        array([0])
        Dimensions without coordinates: test"""
        )

        assert actual == expected


def test_inline_variable_array_repr_custom_repr():
    """
    Generate a string representation of an inline variable array.
    
    This function takes an `xr.Variable` object and a maximum width for the
    representation. It uses the `_repr_inline_` method of the underlying array
    to generate a compact string representation that fits within the specified
    width. If the generated string exceeds the width, it is truncated with '...'.
    
    Parameters:
    -----------
    variable : xr.Variable
    The variable containing the array to be represented.
    max_width
    """

    class CustomArray:
        def __init__(self, value, attr):
            self.value = value
            self.attr = attr

        def _repr_inline_(self, width):
            """
            Generate a string representation of an object with limited width.
            
            Args:
            self (object): The object to be represented.
            width (int): The maximum width of the string representation.
            
            Returns:
            str: A string representation of the object with limited width.
            """

            formatted = f"({self.attr}) {self.value}"
            if len(formatted) > width:
                formatted = f"({self.attr}) ..."

            return formatted

        def __array_function__(self, *args, **kwargs):
            return NotImplemented

        @property
        def shape(self):
            return self.value.shape

        @property
        def dtype(self):
            return self.value.dtype

        @property
        def ndim(self):
            return self.value.ndim

    value = CustomArray(np.array([20, 40]), "m")
    variable = xr.Variable("x", value)

    max_width = 10
    actual = formatting.inline_variable_array_repr(variable, max_width=10)

    assert actual == value._repr_inline_(max_width)


def test_set_numpy_options():
    """
    Set temporary NumPy print options.
    
    Temporarily changes the NumPy print options within the context of the
    function, and restores the original settings after execution.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `np.get_printoptions()`: Retrieves the current NumPy print options.
    - `with formatting.set_numpy_options(threshold=10)`: Temporarily sets the threshold option to 10.
    - `assert len(repr(np
    """

    original_options = np.get_printoptions()
    with formatting.set_numpy_options(threshold=10):
        assert len(repr(np.arange(500))) < 200
    # original options are restored
    assert np.get_printoptions() == original_options


def test_short_numpy_repr():
    """
    Summary line: Test the functionality of the short_numpy_repr function.
    
    This function tests the short_numpy_repr function by creating various
    numpy arrays with different shapes and checking if the number of lines
    in the formatted representation is less than 30.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses numpy to generate random arrays.
    - It checks the number of lines in the formatted representation of each array.
    - The arrays tested have
    """

    cases = [
        np.random.randn(500),
        np.random.randn(20, 20),
        np.random.randn(5, 10, 15),
        np.random.randn(5, 10, 15, 3),
        np.random.randn(100, 5, 1),
    ]
    # number of lines:
    # for default numpy repr: 167, 140, 254, 248, 599
    # for short_numpy_repr: 1, 7, 24, 19, 25
    for array in cases:
        num_lines = formatting.short_numpy_repr(array).count("\n") + 1
        assert num_lines < 30


def test_large_array_repr_length():
    """
    Generate a string representation of a large xarray DataArray and verify its length.
    
    This function creates a random xarray DataArray with dimensions (100, 5, 1),
    then generates a string representation of the array using `repr`. The function
    asserts that the number of lines in the resulting string is less than 50.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the number of lines in the string representation
    """


    da = xr.DataArray(np.random.randn(100, 5, 1))

    result = repr(da).splitlines()
    assert len(result) < 50


@pytest.mark.parametrize(
    "display_max_rows, n_vars, n_attr",
    [(50, 40, 30), (35, 40, 30), (11, 40, 30), (1, 40, 30)],
)
def test__mapping_repr(display_max_rows, n_vars, n_attr):
    """
    Generate a Dataset representation with truncated data variables.
    
    This function creates a :class:`xarray.Dataset` object with specified
    attributes and data variables. It then formats the representation of the
    dataset's data variables, truncating the output based on the `display_max_rows`
    parameter. The function ensures that the summary contains only the relevant
    data variables and does not exceed the specified number of rows.
    
    Parameters:
    display_max_rows (int): The maximum number of rows to
    """

    long_name = "long_name"
    a = np.core.defchararray.add(long_name, np.arange(0, n_vars).astype(str))
    b = np.core.defchararray.add("attr_", np.arange(0, n_attr).astype(str))
    attrs = {k: 2 for k in b}
    coords = dict(time=np.array([0, 1]))
    data_vars = dict()
    for v in a:
        data_vars[v] = xr.DataArray(
            name=v,
            data=np.array([3, 4]),
            dims=["time"],
            coords=coords,
        )
    ds = xr.Dataset(data_vars)
    ds.attrs = attrs

    with xr.set_options(display_max_rows=display_max_rows):

        # Parse the data_vars print and show only data_vars rows:
        summary = formatting.data_vars_repr(ds.data_vars).split("\n")
        summary = [v for v in summary if long_name in v]

        # The length should be less than or equal to display_max_rows:
        len_summary = len(summary)
        data_vars_print_size = min(display_max_rows, len_summary)
        assert len_summary == data_vars_print_size
