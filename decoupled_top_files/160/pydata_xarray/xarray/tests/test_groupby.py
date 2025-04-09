import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.core.groupby import _consolidate_slices

from . import assert_allclose, assert_equal, assert_identical, raises_regex


@pytest.fixture
def dataset():
    """
    Generate a sample dataset using xarray.
    
    This function creates an xarray Dataset with two variables: 'foo' and 'boo'.
    The 'foo' variable is a 3D array with dimensions 'x', 'y', and 'z', while 'boo'
    is a 2D array with dimensions 'z' and 'y'. The values are randomly generated using
    numpy's `randn` function.
    
    Returns:
    xr.Dataset: A dataset containing the variables
    """

    ds = xr.Dataset(
        {"foo": (("x", "y", "z"), np.random.randn(3, 4, 2))},
        {"x": ["a", "b", "c"], "y": [1, 2, 3, 4], "z": [1, 2]},
    )
    ds["boo"] = (("z", "y"), [["f", "g", "h", "j"]] * 2)

    return ds


@pytest.fixture
def array(dataset):
    return dataset["foo"]


def test_consolidate_slices():
    """
    Consolidate overlapping or adjacent slices into a single slice.
    
    Args:
    slices (list): A list of `slice` objects.
    
    Returns:
    list: A list of consolidated `slice` objects.
    
    Raises:
    ValueError: If any non-slice object is found in the input list.
    
    Examples:
    >>> _consolidate_slices([slice(3), slice(3, 5)])
    [slice(5)]
    >>> _consolidate_slices([slice(
    """


    assert _consolidate_slices([slice(3), slice(3, 5)]) == [slice(5)]
    assert _consolidate_slices([slice(2, 3), slice(3, 6)]) == [slice(2, 6)]
    assert _consolidate_slices([slice(2, 3, 1), slice(3, 6, 1)]) == [slice(2, 6, 1)]

    slices = [slice(2, 3), slice(5, 6)]
    assert _consolidate_slices(slices) == slices

    with pytest.raises(ValueError):
        _consolidate_slices([slice(3), 4])


def test_groupby_dims_property(dataset):
    """
    Test the `dims` property of grouped and indexed datasets.
    
    This function checks that the dimensions of a dataset grouped by a specific dimension
    match those of an indexed version of the same dataset. It also verifies that the dimensions
    of a stacked dataset grouped by a combined dimension match those of an indexed version
    of the stacked dataset.
    
    Parameters:
    dataset (xarray.Dataset): The input dataset to be tested.
    
    Returns:
    None: This function does not return any value
    """

    assert dataset.groupby("x").dims == dataset.isel(x=1).dims
    assert dataset.groupby("y").dims == dataset.isel(y=1).dims

    stacked = dataset.stack({"xy": ("x", "y")})
    assert stacked.groupby("xy").dims == stacked.isel(xy=0).dims


def test_multi_index_groupby_map(dataset):
    """
    Apply a mapping function to grouped data along a MultiIndex.
    
    This function tests the ability to apply a mapping function to grouped
    data using a MultiIndex. It stacks the 'x' and 'y' dimensions into a
    single 'space' dimension, groups the data by this dimension, and then
    applies a lambda function that multiplies each value by 2. The result is
    unstacked back into the original 'x' and 'y' dimensions.
    """

    # regression test for GH873
    ds = dataset.isel(z=1, drop=True)[["foo"]]
    expected = 2 * ds
    actual = (
        ds.stack(space=["x", "y"])
        .groupby("space")
        .map(lambda x: 2 * x)
        .unstack("space")
    )
    assert_equal(expected, actual)


def test_multi_index_groupby_sum():
    """
    Test multi-index groupby sum operation.
    
    This function tests the correctness of the `groupby` method with a
    multi-index and the `sum` aggregation function on a xarray Dataset.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The function uses the `xr.Dataset` class from the xarray library to create a dataset with a variable 'foo'.
    - It stacks the 'x' and 'y' dimensions into a single 'space'
    """

    # regression test for GH873
    ds = xr.Dataset(
        {"foo": (("x", "y", "z"), np.ones((3, 4, 2)))},
        {"x": ["a", "b", "c"], "y": [1, 2, 3, 4]},
    )
    expected = ds.sum("z")
    actual = ds.stack(space=["x", "y"]).groupby("space").sum("z").unstack("space")
    assert_equal(expected, actual)


def test_groupby_da_datetime():
    """
    Test grouping and summing a DataArray with datetime indices.
    
    This function tests the `groupby` method on a DataArray with datetime
    indices. The input consists of a DataArray `foo` with datetime coordinates
    and an index array `ind` that categorizes the datetime values into groups.
    The function groups `foo` by the index `ind` and then sums the values within
    each group along the 'time' dimension.
    
    Parameters:
    None
    """

    # test groupby with a DataArray of dtype datetime for GH1132
    # create test data
    times = pd.date_range("2000-01-01", periods=4)
    foo = xr.DataArray([1, 2, 3, 4], coords=dict(time=times), dims="time")
    # create test index
    dd = times.to_pydatetime()
    reference_dates = [dd[0], dd[2]]
    labels = reference_dates[0:1] * 2 + reference_dates[1:2] * 2
    ind = xr.DataArray(
        labels, coords=dict(time=times), dims="time", name="reference_date"
    )
    g = foo.groupby(ind)
    actual = g.sum(dim="time")
    expected = xr.DataArray(
        [3, 7], coords=dict(reference_date=reference_dates), dims="reference_date"
    )
    assert_equal(expected, actual)


def test_groupby_duplicate_coordinate_labels():
    """
    Test grouping by duplicate coordinate labels.
    
    This function checks if the `groupby` method correctly handles duplicate
    coordinate labels in an xarray DataArray. It sums the values along the
    specified coordinate and compares the result with the expected output.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> array = xr.DataArray([1, 2, 3], [("x", [1, 1, 2])])
    >>> expected = xr
    """

    # fix for http://stackoverflow.com/questions/38065129
    array = xr.DataArray([1, 2, 3], [("x", [1, 1, 2])])
    expected = xr.DataArray([3, 3], [("x", [1, 2])])
    actual = array.groupby("x").sum()
    assert_equal(expected, actual)


def test_groupby_input_mutation():
    """
    Test input mutation when using groupby method.
    
    This function verifies that the original DataArray is not modified when
    performing a groupby operation followed by a sum aggregation. The key
    functions used are `groupby` and `sum`. The input DataArray is copied to
    ensure that any modifications during the operation do not affect the
    original data.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the resulting DataArray after the
    """

    # regression test for GH2153
    array = xr.DataArray([1, 2, 3], [("x", [2, 2, 1])])
    array_copy = array.copy()
    expected = xr.DataArray([3, 3], [("x", [1, 2])])
    actual = array.groupby("x").sum()
    assert_identical(expected, actual)
    assert_identical(array, array_copy)  # should not modify inputs


@pytest.mark.parametrize(
    "obj",
    [
        xr.DataArray([1, 2, 3, 4, 5, 6], [("x", [1, 1, 1, 2, 2, 2])]),
        xr.Dataset({"foo": ("x", [1, 2, 3, 4, 5, 6])}, {"x": [1, 1, 1, 2, 2, 2]}),
    ],
)
def test_groupby_map_shrink_groups(obj):
    """
    Group the input object by the 'x' dimension and apply a mapping function that selects specific elements from each group. The resulting groups are then shrunk to include only the first two elements along the 'x' dimension. The function asserts that the resulting object is identical to the expected object after the transformation.
    
    Parameters:
    obj (DataArray or Dataset): The input object to be grouped and transformed.
    
    Returns:
    DataArray or Dataset: The transformed object with groups shrunk to the first
    """

    expected = obj.isel(x=[0, 1, 3, 4])
    actual = obj.groupby("x").map(lambda f: f.isel(x=[0, 1]))
    assert_identical(expected, actual)


@pytest.mark.parametrize(
    "obj",
    [
        xr.DataArray([1, 2, 3], [("x", [1, 2, 2])]),
        xr.Dataset({"foo": ("x", [1, 2, 3])}, {"x": [1, 2, 2]}),
    ],
)
def test_groupby_map_change_group_size(obj):
    """
    Apply a custom function to each group of a grouped xarray object.
    
    This function groups the input xarray object by the 'x' dimension,
    then applies a custom function `func` to each group. The function
    modifies the size of the group and returns a modified group based on
    its size. If the group size is 1, it duplicates the first element;
    otherwise, it keeps only the first element.
    
    Parameters:
    obj (xarray.Dataset or x
    """

    def func(group):
        """
        Selects specific elements from a group based on its size along the 'x' dimension.
        
        Parameters:
        group (xarray.Dataset or xarray.DataArray): The input dataset or array containing dimensions including 'x'.
        
        Returns:
        xarray.Dataset or xarray.DataArray: A subset of the input group with selected elements along the 'x' dimension.
        
        Notes:
        - If the size of the 'x' dimension is 1, the first two elements are selected and
        """

        if group.sizes["x"] == 1:
            result = group.isel(x=[0, 0])
        else:
            result = group.isel(x=[0])
        return result

    expected = obj.isel(x=[0, 0, 1])
    actual = obj.groupby("x").map(func)
    assert_identical(expected, actual)


def test_da_groupby_map_func_args():
    """
    Apply a custom function to grouped data along the 'x' dimension.
    
    This function groups the input DataArray by the 'x' dimension and applies
    a custom function `func` to each group. The custom function `func` takes
    three arguments: `arg1`, `arg2`, and `arg3`. The function is applied with
    `arg2` fixed at 1 and `arg3` set to 1. The result is a new DataArray with
    """

    def func(arg1, arg2, arg3=0):
        return arg1 + arg2 + arg3

    array = xr.DataArray([1, 1, 1], [("x", [1, 2, 3])])
    expected = xr.DataArray([3, 3, 3], [("x", [1, 2, 3])])
    actual = array.groupby("x").map(func, args=(1,), arg3=1)
    assert_identical(expected, actual)


def test_ds_groupby_map_func_args():
    """
    Apply a custom function to each group of a dataset grouped by a dimension.
    
    Args:
    dataset (xr.Dataset): The input dataset containing the data to be processed.
    func (callable): The custom function to apply to each group.
    args (tuple, optional): Positional arguments to pass to the custom function.
    arg3 (int, optional): An additional keyword argument to pass to the custom function.
    
    Returns:
    xr.Dataset: A new dataset with the results of applying the
    """

    def func(arg1, arg2, arg3=0):
        return arg1 + arg2 + arg3

    dataset = xr.Dataset({"foo": ("x", [1, 1, 1])}, {"x": [1, 2, 3]})
    expected = xr.Dataset({"foo": ("x", [3, 3, 3])}, {"x": [1, 2, 3]})
    actual = dataset.groupby("x").map(func, args=(1,), arg3=1)
    assert_identical(expected, actual)


def test_da_groupby_empty():
    """
    Test that attempting to groupby an empty DataArray raises a ValueError.
    
    This function tests whether attempting to groupby an empty DataArray
    (created using `xr.DataArray([])` with dimension "dim") raises a ValueError.
    """


    empty_array = xr.DataArray([], dims="dim")

    with pytest.raises(ValueError):
        empty_array.groupby("dim")


def test_da_groupby_quantile():
    """
    Compute quantiles of a DataArray along specified dimensions or groups.
    
    This function calculates quantiles for a given DataArray either across all dimensions or within specific groups defined by the 'x' coordinate. It supports both scalar and vector quantiles and can handle multiple dimensions.
    
    Parameters:
    array (xr.DataArray): The input DataArray containing the data to compute quantiles on.
    
    Returns:
    xr.DataArray: A new DataArray with the computed quantiles.
    
    Examples:
    -
    """


    array = xr.DataArray(
        data=[1, 2, 3, 4, 5, 6], coords={"x": [1, 1, 1, 2, 2, 2]}, dims="x"
    )

    # Scalar quantile
    expected = xr.DataArray(
        data=[2, 5], coords={"x": [1, 2], "quantile": 0.5}, dims="x"
    )
    actual = array.groupby("x").quantile(0.5)
    assert_identical(expected, actual)

    # Vector quantile
    expected = xr.DataArray(
        data=[[1, 3], [4, 6]],
        coords={"x": [1, 2], "quantile": [0, 1]},
        dims=("x", "quantile"),
    )
    actual = array.groupby("x").quantile([0, 1])
    assert_identical(expected, actual)

    # Multiple dimensions
    array = xr.DataArray(
        data=[[1, 11, 26], [2, 12, 22], [3, 13, 23], [4, 16, 24], [5, 15, 25]],
        coords={"x": [1, 1, 1, 2, 2], "y": [0, 0, 1]},
        dims=("x", "y"),
    )

    actual_x = array.groupby("x").quantile(0, dim=...)
    expected_x = xr.DataArray(
        data=[1, 4], coords={"x": [1, 2], "quantile": 0}, dims="x"
    )
    assert_identical(expected_x, actual_x)

    actual_y = array.groupby("y").quantile(0, dim=...)
    expected_y = xr.DataArray(
        data=[1, 22], coords={"y": [0, 1], "quantile": 0}, dims="y"
    )
    assert_identical(expected_y, actual_y)

    actual_xx = array.groupby("x").quantile(0)
    expected_xx = xr.DataArray(
        data=[[1, 11, 22], [4, 15, 24]],
        coords={"x": [1, 2], "y": [0, 0, 1], "quantile": 0},
        dims=("x", "y"),
    )
    assert_identical(expected_xx, actual_xx)

    actual_yy = array.groupby("y").quantile(0)
    expected_yy = xr.DataArray(
        data=[[1, 26], [2, 22], [3, 23], [4, 24], [5, 25]],
        coords={"x": [1, 1, 1, 2, 2], "y": [0, 1], "quantile": 0},
        dims=("x", "y"),
    )
    assert_identical(expected_yy, actual_yy)

    times = pd.date_range("2000-01-01", periods=365)
    x = [0, 1]
    foo = xr.DataArray(
        np.reshape(np.arange(365 * 2), (365, 2)),
        coords={"time": times, "x": x},
        dims=("time", "x"),
    )
    g = foo.groupby(foo.time.dt.month)

    actual = g.quantile(0, dim=...)
    expected = xr.DataArray(
        data=[
            0.0,
            62.0,
            120.0,
            182.0,
            242.0,
            304.0,
            364.0,
            426.0,
            488.0,
            548.0,
            610.0,
            670.0,
        ],
        coords={"month": np.arange(1, 13), "quantile": 0},
        dims="month",
    )
    assert_identical(expected, actual)

    actual = g.quantile(0, dim="time")[:2]
    expected = xr.DataArray(
        data=[[0.0, 1], [62.0, 63]],
        coords={"month": [1, 2], "x": [0, 1], "quantile": 0},
        dims=("month", "x"),
    )
    assert_identical(expected, actual)


def test_ds_groupby_quantile():
    """
    Compute quantiles of a dataset grouped by a dimension.
    
    This function groups a dataset by a specified dimension and computes the
    quantiles of the grouped data. It supports both scalar and vector quantiles,
    as well as multiple dimensions. The function can handle datasets with
    different dimensions and coordinates.
    
    Parameters:
    ds (xarray.Dataset): Input dataset containing the data to be grouped and
    quantiled.
    
    Returns:
    xarray.Dataset: A new dataset containing the computed
    """

    ds = xr.Dataset(
        data_vars={"a": ("x", [1, 2, 3, 4, 5, 6])}, coords={"x": [1, 1, 1, 2, 2, 2]}
    )

    # Scalar quantile
    expected = xr.Dataset(
        data_vars={"a": ("x", [2, 5])}, coords={"quantile": 0.5, "x": [1, 2]}
    )
    actual = ds.groupby("x").quantile(0.5)
    assert_identical(expected, actual)

    # Vector quantile
    expected = xr.Dataset(
        data_vars={"a": (("x", "quantile"), [[1, 3], [4, 6]])},
        coords={"x": [1, 2], "quantile": [0, 1]},
    )
    actual = ds.groupby("x").quantile([0, 1])
    assert_identical(expected, actual)

    # Multiple dimensions
    ds = xr.Dataset(
        data_vars={
            "a": (
                ("x", "y"),
                [[1, 11, 26], [2, 12, 22], [3, 13, 23], [4, 16, 24], [5, 15, 25]],
            )
        },
        coords={"x": [1, 1, 1, 2, 2], "y": [0, 0, 1]},
    )

    actual_x = ds.groupby("x").quantile(0, dim=...)
    expected_x = xr.Dataset({"a": ("x", [1, 4])}, coords={"x": [1, 2], "quantile": 0})
    assert_identical(expected_x, actual_x)

    actual_y = ds.groupby("y").quantile(0, dim=...)
    expected_y = xr.Dataset({"a": ("y", [1, 22])}, coords={"y": [0, 1], "quantile": 0})
    assert_identical(expected_y, actual_y)

    actual_xx = ds.groupby("x").quantile(0)
    expected_xx = xr.Dataset(
        {"a": (("x", "y"), [[1, 11, 22], [4, 15, 24]])},
        coords={"x": [1, 2], "y": [0, 0, 1], "quantile": 0},
    )
    assert_identical(expected_xx, actual_xx)

    actual_yy = ds.groupby("y").quantile(0)
    expected_yy = xr.Dataset(
        {"a": (("x", "y"), [[1, 26], [2, 22], [3, 23], [4, 24], [5, 25]])},
        coords={"x": [1, 1, 1, 2, 2], "y": [0, 1], "quantile": 0},
    ).transpose()
    assert_identical(expected_yy, actual_yy)

    times = pd.date_range("2000-01-01", periods=365)
    x = [0, 1]
    foo = xr.Dataset(
        {"a": (("time", "x"), np.reshape(np.arange(365 * 2), (365, 2)))},
        coords=dict(time=times, x=x),
    )
    g = foo.groupby(foo.time.dt.month)

    actual = g.quantile(0, dim=...)
    expected = xr.Dataset(
        {
            "a": (
                "month",
                [
                    0.0,
                    62.0,
                    120.0,
                    182.0,
                    242.0,
                    304.0,
                    364.0,
                    426.0,
                    488.0,
                    548.0,
                    610.0,
                    670.0,
                ],
            )
        },
        coords={"month": np.arange(1, 13), "quantile": 0},
    )
    assert_identical(expected, actual)

    actual = g.quantile(0, dim="time").isel(month=slice(None, 2))
    expected = xr.Dataset(
        data_vars={"a": (("month", "x"), [[0.0, 1], [62.0, 63]])},
        coords={"month": [1, 2], "x": [0, 1], "quantile": 0},
    )
    assert_identical(expected, actual)


def test_da_groupby_assign_coords():
    """
    Group a DataArray by a dimension and assign new coordinates to the grouped result.
    
    This function groups a given DataArray by a specified dimension and assigns new coordinates to each group. The resulting DataArray will have the assigned coordinates along with the original dimensions.
    
    Parameters:
    None (The function uses predefined DataArrays)
    
    Returns:
    None (The function asserts the equality of the expected and actual results)
    
    Important Functions:
    - `groupby`: Groups the DataArray by a specified
    """

    actual = xr.DataArray(
        [[3, 4, 5], [6, 7, 8]], dims=["y", "x"], coords={"y": range(2), "x": range(3)}
    )
    actual1 = actual.groupby("x").assign_coords({"y": [-1, -2]})
    actual2 = actual.groupby("x").assign_coords(y=[-1, -2])
    expected = xr.DataArray(
        [[3, 4, 5], [6, 7, 8]], dims=["y", "x"], coords={"y": [-1, -2], "x": range(3)}
    )
    assert_identical(expected, actual1)
    assert_identical(expected, actual2)


repr_da = xr.DataArray(
    np.random.randn(10, 20, 6, 24),
    dims=["x", "y", "z", "t"],
    coords={
        "z": ["a", "b", "c", "a", "b", "c"],
        "x": [1, 1, 1, 2, 2, 3, 4, 5, 3, 4],
        "t": pd.date_range("2001-01-01", freq="M", periods=24),
        "month": ("t", list(range(1, 13)) * 2),
    },
)


@pytest.mark.parametrize("dim", ["x", "y", "z", "month"])
@pytest.mark.parametrize("obj", [repr_da, repr_da.to_dataset(name="a")])
def test_groupby_repr(obj, dim):
    """
    Generate a grouped representation of an object based on a specified dimension.
    
    Parameters:
    obj (object): The input object to be grouped.
    dim (str): The dimension or label to group the object by.
    
    Returns:
    str: A string representation of the grouped object.
    
    Notes:
    - The function uses the `groupby` method from the input object's class.
    - The expected output includes details about the grouping, such as the number of groups, their labels, and
    """

    actual = repr(obj.groupby(dim))
    expected = "%sGroupBy" % obj.__class__.__name__
    expected += ", grouped over %r " % dim
    expected += "\n%r groups with labels " % (len(np.unique(obj[dim])))
    if dim == "x":
        expected += "1, 2, 3, 4, 5."
    elif dim == "y":
        expected += "0, 1, 2, 3, 4, 5, ..., 15, 16, 17, 18, 19."
    elif dim == "z":
        expected += "'a', 'b', 'c'."
    elif dim == "month":
        expected += "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12."
    assert actual == expected


@pytest.mark.parametrize("obj", [repr_da, repr_da.to_dataset(name="a")])
def test_groupby_repr_datetime(obj):
    """
    Generate a GroupBy object for a pandas DataFrame or Series based on the month of a datetime column.
    
    Parameters:
    obj (pandas.DataFrame or pandas.Series): The input data containing a datetime column named 't'.
    
    Returns:
    str: A string representation of the GroupBy object, indicating the grouping is done by the month of the 't' column and listing the number of unique months present in the data.
    
    Example:
    >>> df = pd.DataFrame({'t': pd.date_range
    """

    actual = repr(obj.groupby("t.month"))
    expected = "%sGroupBy" % obj.__class__.__name__
    expected += ", grouped over 'month' "
    expected += "\n%r groups with labels " % (len(np.unique(obj.t.dt.month)))
    expected += "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12."
    assert actual == expected


def test_groupby_drops_nans():
    """
    Test the behavior of `groupby` when applied to datasets containing NaN values.
    
    This function tests various operations on a dataset with NaN values in different
    contexts, including non-reduction operations, reduction along grouped dimensions,
    reduction along different dimensions, and handling of NaNs and NaTs in non-dimensional
    coordinates. The function uses the `xr.Dataset` and `xr.DataArray` classes from the
    xarray library to create and manipulate the dataset.
    
    Parameters:
    None
    """

    # GH2383
    # nan in 2D data variable (requires stacking)
    ds = xr.Dataset(
        {
            "variable": (("lat", "lon", "time"), np.arange(60.0).reshape((4, 3, 5))),
            "id": (("lat", "lon"), np.arange(12.0).reshape((4, 3))),
        },
        coords={"lat": np.arange(4), "lon": np.arange(3), "time": np.arange(5)},
    )

    ds["id"].values[0, 0] = np.nan
    ds["id"].values[3, 0] = np.nan
    ds["id"].values[-1, -1] = np.nan

    grouped = ds.groupby(ds.id)

    # non reduction operation
    expected = ds.copy()
    expected.variable.values[0, 0, :] = np.nan
    expected.variable.values[-1, -1, :] = np.nan
    expected.variable.values[3, 0, :] = np.nan
    actual = grouped.map(lambda x: x).transpose(*ds.variable.dims)
    assert_identical(actual, expected)

    # reduction along grouped dimension
    actual = grouped.mean()
    stacked = ds.stack({"xy": ["lat", "lon"]})
    expected = (
        stacked.variable.where(stacked.id.notnull()).rename({"xy": "id"}).to_dataset()
    )
    expected["id"] = stacked.id.values
    assert_identical(actual, expected.dropna("id").transpose(*actual.dims))

    # reduction operation along a different dimension
    actual = grouped.mean("time")
    expected = ds.mean("time").where(ds.id.notnull())
    assert_identical(actual, expected)

    # NaN in non-dimensional coordinate
    array = xr.DataArray([1, 2, 3], [("x", [1, 2, 3])])
    array["x1"] = ("x", [1, 1, np.nan])
    expected = xr.DataArray(3, [("x1", [1])])
    actual = array.groupby("x1").sum()
    assert_equal(expected, actual)

    # NaT in non-dimensional coordinate
    array["t"] = (
        "x",
        [
            np.datetime64("2001-01-01"),
            np.datetime64("2001-01-01"),
            np.datetime64("NaT"),
        ],
    )
    expected = xr.DataArray(3, [("t", [np.datetime64("2001-01-01")])])
    actual = array.groupby("t").sum()
    assert_equal(expected, actual)

    # test for repeated coordinate labels
    array = xr.DataArray([0, 1, 2, 4, 3, 4], [("x", [np.nan, 1, 1, np.nan, 2, np.nan])])
    expected = xr.DataArray([3, 3], [("x", [1, 2])])
    actual = array.groupby("x").sum()
    assert_equal(expected, actual)


def test_groupby_grouping_errors():
    """
    Test errors raised by grouping operations.
    
    This function tests various scenarios where grouping operations on an
    xarray Dataset or DataArray should raise specific errors. The key functions
    involved are `groupby` and `groupby_bins`, which are used to group data
    based on specified criteria. The inputs include a Dataset with a variable
    'foo' and coordinates 'x', and a DataArray converted from this Dataset.
    
    Parameters:
    None
    
    Returns:
    None
    """

    dataset = xr.Dataset({"foo": ("x", [1, 1, 1])}, {"x": [1, 2, 3]})
    with raises_regex(ValueError, "None of the data falls within bins with edges"):
        dataset.groupby_bins("x", bins=[0.1, 0.2, 0.3])

    with raises_regex(ValueError, "None of the data falls within bins with edges"):
        dataset.to_array().groupby_bins("x", bins=[0.1, 0.2, 0.3])

    with raises_regex(ValueError, "All bin edges are NaN."):
        dataset.groupby_bins("x", bins=[np.nan, np.nan, np.nan])

    with raises_regex(ValueError, "All bin edges are NaN."):
        dataset.to_array().groupby_bins("x", bins=[np.nan, np.nan, np.nan])

    with raises_regex(ValueError, "Failed to group data."):
        dataset.groupby(dataset.foo * np.nan)

    with raises_regex(ValueError, "Failed to group data."):
        dataset.to_array().groupby(dataset.foo * np.nan)


def test_groupby_reduce_dimension_error(array):
    """
    Group the input array by the 'y' dimension and compute the mean along specified dimensions. If the 'y' dimension is not provided, or if an invalid dimension is given, raise a ValueError indicating that reduction operations are not allowed over multiple dimensions.
    
    Parameters:
    -----------
    array : xarray.DataArray
    The input array to be grouped and reduced.
    
    Returns:
    --------
    DataArray or Dataset
    - If no error occurs: The mean of the grouped data along the
    """

    grouped = array.groupby("y")
    with raises_regex(ValueError, "cannot reduce over dimensions"):
        grouped.mean()

    with raises_regex(ValueError, "cannot reduce over dimensions"):
        grouped.mean("huh")

    with raises_regex(ValueError, "cannot reduce over dimensions"):
        grouped.mean(("x", "y", "asd"))

    grouped = array.groupby("y", squeeze=False)
    assert_identical(array, grouped.mean())

    assert_identical(array.mean("x"), grouped.reduce(np.mean, "x"))
    assert_allclose(array.mean(["x", "z"]), grouped.reduce(np.mean, ["x", "z"]))


def test_groupby_multiple_string_args(array):
    with pytest.raises(TypeError):
        array.groupby("x", "y")


def test_groupby_bins_timeseries():
    """
    Group by time bins and sum values in a timeseries dataset.
    
    This function takes a dataset containing a 'time' dimension and a 'val'
    dimension, groups the data by time bins of 24 hours, and sums the values
    within each bin. The resulting dataset contains the summed values for each
    time bin.
    
    Parameters:
    None
    
    Returns:
    - `actual`: A Dataset with the summed values for each time bin.
    - `expected`: A
    """

    ds = xr.Dataset()
    ds["time"] = xr.DataArray(
        pd.date_range("2010-08-01", "2010-08-15", freq="15min"), dims="time"
    )
    ds["val"] = xr.DataArray(np.ones(*ds["time"].shape), dims="time")
    time_bins = pd.date_range(start="2010-08-01", end="2010-08-15", freq="24H")
    actual = ds.groupby_bins("time", time_bins).sum()
    expected = xr.DataArray(
        96 * np.ones((14,)),
        dims=["time_bins"],
        coords={"time_bins": pd.cut(time_bins, time_bins).categories},
    ).to_dataset(name="val")
    assert_identical(actual, expected)


def test_groupby_none_group_name():
    """
    Calculate the mean of a DataArray grouped by another DataArray.
    
    This function takes a DataArray `da` with no name attribute and groups it by
    another DataArray `key`. It then computes the mean along the grouped dimension.
    
    Parameters:
    None
    
    Returns:
    mean (DataArray): The mean values of `da` after grouping by `key`.
    
    Notes:
    - The input `da` is a DataArray without a name attribute.
    - The input
    """

    # GH158
    # xarray should not fail if a DataArray's name attribute is None

    data = np.arange(10) + 10
    da = xr.DataArray(data)  # da.name = None
    key = xr.DataArray(np.floor_divide(data, 2))

    mean = da.groupby(key).mean()
    assert "group" in mean.dims


def test_groupby_getitem(dataset):
    """
    Group by a dimension and select specific data variables.
    
    This function groups the dataset by a specified dimension and selects
    specific data variables using the `sel` method. It supports selecting
    individual values or slices along dimensions.
    
    Parameters:
    dataset (xarray.Dataset): The input dataset to be grouped and sliced.
    
    Returns:
    xarray.Dataset: A new dataset with the selected and grouped data.
    
    Examples:
    >>> assert_identical(dataset.sel(x="a"), dataset.groupby("
    """


    assert_identical(dataset.sel(x="a"), dataset.groupby("x")["a"])
    assert_identical(dataset.sel(z=1), dataset.groupby("z")[1])

    assert_identical(dataset.foo.sel(x="a"), dataset.foo.groupby("x")["a"])
    assert_identical(dataset.foo.sel(z=1), dataset.foo.groupby("z")[1])

    actual = dataset.groupby("boo")["f"].unstack().transpose("x", "y", "z")
    expected = dataset.sel(y=[1], z=[1, 2]).transpose("x", "y", "z")
    assert_identical(expected, actual)


# TODO: move other groupby tests from test_dataset and test_dataarray over here
