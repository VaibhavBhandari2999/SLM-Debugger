import pytest

import xarray
from xarray import concat, merge
from xarray.backends.file_manager import FILE_CACHE
from xarray.core.options import OPTIONS, _get_keep_attrs
from xarray.tests.test_dataset import create_test_data


def test_invalid_option_raises():
    with pytest.raises(ValueError):
        xarray.set_options(not_a_valid_options=True)


def test_display_width():
    """
    Set the display width for printing datasets and data arrays.
    
    This function configures the display width for printing datasets and data arrays. It raises a ValueError if the provided display width is not a positive integer.
    
    Parameters:
    display_width (int): The width to use for printing datasets and data arrays.
    
    Raises:
    ValueError: If the provided display width is not a positive integer.
    """

    with pytest.raises(ValueError):
        xarray.set_options(display_width=0)
    with pytest.raises(ValueError):
        xarray.set_options(display_width=-10)
    with pytest.raises(ValueError):
        xarray.set_options(display_width=3.5)


def test_arithmetic_join():
    """
    Set the arithmetic join behavior for xarray operations.
    
    This function sets the arithmetic join behavior for xarray operations. It can be used to control how coordinates are handled when performing arithmetic operations on datasets or dataarrays.
    
    Parameters:
    arithmetic_join (str): The arithmetic join behavior to set. Must be one of "exact" (default).
    
    Returns:
    None: This function does not return anything. It sets the global options for xarray.
    
    Raises:
    ValueError: If the provided arithmetic_join value is
    """

    with pytest.raises(ValueError):
        xarray.set_options(arithmetic_join="invalid")
    with xarray.set_options(arithmetic_join="exact"):
        assert OPTIONS["arithmetic_join"] == "exact"


def test_enable_cftimeindex():
    with pytest.raises(ValueError):
        xarray.set_options(enable_cftimeindex=None)
    with pytest.warns(FutureWarning, match="no-op"):
        with xarray.set_options(enable_cftimeindex=True):
            assert OPTIONS["enable_cftimeindex"]


def test_file_cache_maxsize():
    """
    Set the maximum size of the file cache.
    
    This function sets the maximum size of the file cache used by xarray. If the cache exceeds this size, the least recently used items will be removed to make space.
    
    Parameters:
    file_cache_maxsize (int): The maximum size of the file cache.
    
    Raises:
    ValueError: If the provided file_cache_maxsize is less than 1.
    
    Note:
    The function temporarily changes the file cache maxsize within the context of a 'with' statement
    """

    with pytest.raises(ValueError):
        xarray.set_options(file_cache_maxsize=0)
    original_size = FILE_CACHE.maxsize
    with xarray.set_options(file_cache_maxsize=123):
        assert FILE_CACHE.maxsize == 123
    assert FILE_CACHE.maxsize == original_size


def test_keep_attrs():
    with pytest.raises(ValueError):
        xarray.set_options(keep_attrs="invalid_str")
    with xarray.set_options(keep_attrs=True):
        assert OPTIONS["keep_attrs"]
    with xarray.set_options(keep_attrs=False):
        assert not OPTIONS["keep_attrs"]
    with xarray.set_options(keep_attrs="default"):
        assert _get_keep_attrs(default=True)
        assert not _get_keep_attrs(default=False)


def test_nested_options():
    """
    Set and reset the display width for xarray objects.
    
    This function temporarily sets the display width for xarray objects and ensures that the original display width is restored after the nested blocks.
    
    Parameters:
    display_width (int): The new display width to be set temporarily.
    
    Key behavior:
    - The original display width is saved at the start.
    - The display width is set to the specified value within the first block.
    - The display width is set to a new specified value within the nested block.
    - After
    """

    original = OPTIONS["display_width"]
    with xarray.set_options(display_width=1):
        assert OPTIONS["display_width"] == 1
        with xarray.set_options(display_width=2):
            assert OPTIONS["display_width"] == 2
        assert OPTIONS["display_width"] == 1
    assert OPTIONS["display_width"] == original


def test_display_style():
    original = "html"
    assert OPTIONS["display_style"] == original
    with pytest.raises(ValueError):
        xarray.set_options(display_style="invalid_str")
    with xarray.set_options(display_style="text"):
        assert OPTIONS["display_style"] == "text"
    assert OPTIONS["display_style"] == original


def create_test_dataset_attrs(seed=0):
    """
    Generate a test dataset with predefined attributes.
    
    This function creates a test dataset using `create_test_data` and assigns specific attributes to it.
    
    Parameters:
    seed (int, optional): Seed value for reproducibility. Default is 0.
    
    Returns:
    xarray.Dataset: A test dataset with attributes "attr1", "attr2", and "attr3".
    
    Example:
    >>> ds = create_test_dataset_attrs(42)
    >>> ds.attrs
    {'attr1': 5,
    """

    ds = create_test_data(seed)
    ds.attrs = {"attr1": 5, "attr2": "history", "attr3": {"nested": "more_info"}}
    return ds


def create_test_dataarray_attrs(seed=0, var="var1"):
    """
    Generate a DataArray with specified attributes.
    
    This function creates a DataArray from test data and assigns specific attributes to it.
    
    Parameters:
    seed (int, optional): Seed value for the random number generator to ensure reproducibility. Default is 0.
    var (str, optional): Variable name to extract from the test data. Default is "var1".
    
    Returns:
    xarray.DataArray: A DataArray with assigned attributes.
    
    Attributes assigned to the DataArray:
    - attr1 (
    """

    da = create_test_data(seed)[var]
    da.attrs = {"attr1": 5, "attr2": "history", "attr3": {"nested": "more_info"}}
    return da


class TestAttrRetention:
    def test_dataset_attr_retention(self):
        # Use .mean() for all tests: a typical reduction operation
        ds = create_test_dataset_attrs()
        original_attrs = ds.attrs

        # Test default behaviour
        result = ds.mean()
        assert result.attrs == {}
        with xarray.set_options(keep_attrs="default"):
            result = ds.mean()
            assert result.attrs == {}

        with xarray.set_options(keep_attrs=True):
            result = ds.mean()
            assert result.attrs == original_attrs

        with xarray.set_options(keep_attrs=False):
            result = ds.mean()
            assert result.attrs == {}

    def test_dataarray_attr_retention(self):
        # Use .mean() for all tests: a typical reduction operation
        da = create_test_dataarray_attrs()
        original_attrs = da.attrs

        # Test default behaviour
        result = da.mean()
        assert result.attrs == {}
        with xarray.set_options(keep_attrs="default"):
            result = da.mean()
            assert result.attrs == {}

        with xarray.set_options(keep_attrs=True):
            result = da.mean()
            assert result.attrs == original_attrs

        with xarray.set_options(keep_attrs=False):
            result = da.mean()
            assert result.attrs == {}

    def test_groupby_attr_retention(self):
        """
        Tests the retention of attributes when grouping and aggregating a DataArray.
        
        This function checks how attributes are retained when a DataArray is grouped and aggregated using the `groupby` and `sum` methods. The behavior is tested under different settings for the `keep_attrs` option.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a DataArray `da` with predefined attributes.
        - It tests the default behavior of attribute retention.
        - It also tests
        """

        da = xarray.DataArray([1, 2, 3], [("x", [1, 1, 2])])
        da.attrs = {"attr1": 5, "attr2": "history", "attr3": {"nested": "more_info"}}
        original_attrs = da.attrs

        # Test default behaviour
        result = da.groupby("x").sum(keep_attrs=True)
        assert result.attrs == original_attrs
        with xarray.set_options(keep_attrs="default"):
            result = da.groupby("x").sum(keep_attrs=True)
            assert result.attrs == original_attrs

        with xarray.set_options(keep_attrs=True):
            result1 = da.groupby("x")
            result = result1.sum()
            assert result.attrs == original_attrs

        with xarray.set_options(keep_attrs=False):
            result = da.groupby("x").sum()
            assert result.attrs == {}

    def test_concat_attr_retention(self):
        ds1 = create_test_dataset_attrs()
        ds2 = create_test_dataset_attrs()
        ds2.attrs = {"wrong": "attributes"}
        original_attrs = ds1.attrs

        # Test default behaviour of keeping the attrs of the first
        # dataset in the supplied list
        # global keep_attrs option current doesn't affect concat
        result = concat([ds1, ds2], dim="dim1")
        assert result.attrs == original_attrs

    @pytest.mark.xfail
    def test_merge_attr_retention(self):
        da1 = create_test_dataarray_attrs(var="var1")
        da2 = create_test_dataarray_attrs(var="var2")
        da2.attrs = {"wrong": "attributes"}
        original_attrs = da1.attrs

        # merge currently discards attrs, and the global keep_attrs
        # option doesn't affect this
        result = merge([da1, da2])
        assert result.attrs == original_attrs

    def test_display_style_text(self):
        ds = create_test_dataset_attrs()
        with xarray.set_options(display_style="text"):
            text = ds._repr_html_()
            assert text.startswith("<pre>")
            assert "&#x27;nested&#x27;" in text
            assert "&lt;xarray.Dataset&gt;" in text

    def test_display_style_html(self):
        ds = create_test_dataset_attrs()
        with xarray.set_options(display_style="html"):
            html = ds._repr_html_()
            assert html.startswith("<div>")
            assert "&#x27;nested&#x27;" in html

    def test_display_dataarray_style_text(self):
        da = create_test_dataarray_attrs()
        with xarray.set_options(display_style="text"):
            text = da._repr_html_()
            assert text.startswith("<pre>")
            assert "&lt;xarray.DataArray &#x27;var1&#x27;" in text

    def test_display_dataarray_style_html(self):
        da = create_test_dataarray_attrs()
        with xarray.set_options(display_style="html"):
            html = da._repr_html_()
            assert html.startswith("<div>")
            assert "#x27;nested&#x27;" in html
27;" in html
