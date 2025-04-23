import numpy as np
import pytest

import xarray as xr
from xarray import DataArray
from xarray.tests import assert_allclose, assert_equal, raises_regex


@pytest.mark.parametrize("as_dataset", (True, False))
def test_weighted_non_DataArray_weights(as_dataset):

    data = DataArray([1, 2])
    if as_dataset:
        data = data.to_dataset(name="data")

    with raises_regex(ValueError, "`weights` must be a DataArray"):
        data.weighted([1, 2])


@pytest.mark.parametrize("as_dataset", (True, False))
@pytest.mark.parametrize("weights", ([np.nan, 2], [np.nan, np.nan]))
def test_weighted_weights_nan_raises(as_dataset, weights):
    """
    Test that the `weighted` method raises a ValueError when `weights` contain missing values (NaNs).
    
    Parameters:
    as_dataset (bool): If True, the input `data` is converted to a dataset before calling `weighted`.
    weights (array-like): The weights to be applied to the data.
    
    Returns:
    None: The function is expected to raise a ValueError.
    
    Raises:
    ValueError: If `weights` contains missing values (NaNs).
    """


    data = DataArray([1, 2])
    if as_dataset:
        data = data.to_dataset(name="data")

    with pytest.raises(ValueError, match="`weights` cannot contain missing values."):
        data.weighted(DataArray(weights))


@pytest.mark.parametrize(
    ("weights", "expected"),
    (([1, 2], 3), ([2, 0], 2), ([0, 0], np.nan), ([-1, 1], np.nan)),
)
def test_weighted_sum_of_weights_no_nan(weights, expected):

    da = DataArray([1, 2])
    weights = DataArray(weights)
    result = da.weighted(weights).sum_of_weights()

    expected = DataArray(expected)

    assert_equal(expected, result)


@pytest.mark.parametrize(
    ("weights", "expected"),
    (([1, 2], 2), ([2, 0], np.nan), ([0, 0], np.nan), ([-1, 1], 1)),
)
def test_weighted_sum_of_weights_nan(weights, expected):

    da = DataArray([np.nan, 2])
    weights = DataArray(weights)
    result = da.weighted(weights).sum_of_weights()

    expected = DataArray(expected)

    assert_equal(expected, result)


def test_weighted_sum_of_weights_bool():
    # https://github.com/pydata/xarray/issues/4074

    da = DataArray([1, 2])
    weights = DataArray([True, True])
    result = da.weighted(weights).sum_of_weights()

    expected = DataArray(2)

    assert_equal(expected, result)


@pytest.mark.parametrize("da", ([1.0, 2], [1, np.nan], [np.nan, np.nan]))
@pytest.mark.parametrize("factor", [0, 1, 3.14])
@pytest.mark.parametrize("skipna", (True, False))
def test_weighted_sum_equal_weights(da, factor, skipna):
    # if all weights are 'f'; weighted sum is f times the ordinary sum

    da = DataArray(da)
    weights = xr.full_like(da, factor)

    expected = da.sum(skipna=skipna) * factor
    result = da.weighted(weights).sum(skipna=skipna)

    assert_equal(expected, result)


@pytest.mark.parametrize(
    ("weights", "expected"), (([1, 2], 5), ([0, 2], 4), ([0, 0], 0))
)
def test_weighted_sum_no_nan(weights, expected):
    """
    Test the weighted sum of a DataArray with specified weights.
    
    Parameters:
    weights (list or numpy array): The weights to apply to each element of the DataArray.
    expected (list or numpy array): The expected result after applying the weighted sum.
    
    This function creates a DataArray with values [1, 2] and applies the weighted sum operation using the provided weights. The result is then compared to the expected output using an assertion.
    """


    da = DataArray([1, 2])

    weights = DataArray(weights)
    result = da.weighted(weights).sum()
    expected = DataArray(expected)

    assert_equal(expected, result)


@pytest.mark.parametrize(
    ("weights", "expected"), (([1, 2], 4), ([0, 2], 4), ([1, 0], 0), ([0, 0], 0))
)
@pytest.mark.parametrize("skipna", (True, False))
def test_weighted_sum_nan(weights, expected, skipna):

    da = DataArray([np.nan, 2])

    weights = DataArray(weights)
    result = da.weighted(weights).sum(skipna=skipna)

    if skipna:
        expected = DataArray(expected)
    else:
        expected = DataArray(np.nan)

    assert_equal(expected, result)


@pytest.mark.filterwarnings("ignore:Mean of empty slice")
@pytest.mark.parametrize("da", ([1.0, 2], [1, np.nan], [np.nan, np.nan]))
@pytest.mark.parametrize("skipna", (True, False))
@pytest.mark.parametrize("factor", [1, 2, 3.14])
def test_weighted_mean_equal_weights(da, skipna, factor):
    """
    Compute the weighted mean of the data array with all weights equal to a given factor.
    
    Parameters:
    da (DataArray): The input data array.
    skipna (bool): If True, skip missing values (NaNs) for the purpose of the calculation.
    factor (float): The value to which all weights are set.
    
    Returns:
    DataArray: The weighted mean of the input data array.
    
    Notes:
    If all weights are equal and non-zero, the result should be the same
    """

    # if all weights are equal (!= 0), should yield the same result as mean

    da = DataArray(da)

    # all weights as 1.
    weights = xr.full_like(da, factor)

    expected = da.mean(skipna=skipna)
    result = da.weighted(weights).mean(skipna=skipna)

    assert_equal(expected, result)


@pytest.mark.parametrize(
    ("weights", "expected"), (([4, 6], 1.6), ([1, 0], 1.0), ([0, 0], np.nan))
)
def test_weighted_mean_no_nan(weights, expected):

    da = DataArray([1, 2])
    weights = DataArray(weights)
    expected = DataArray(expected)

    result = da.weighted(weights).mean()

    assert_equal(expected, result)


@pytest.mark.parametrize(
    ("weights", "expected"), (([4, 6], 2.0), ([1, 0], np.nan), ([0, 0], np.nan))
)
@pytest.mark.parametrize("skipna", (True, False))
def test_weighted_mean_nan(weights, expected, skipna):

    da = DataArray([np.nan, 2])
    weights = DataArray(weights)

    if skipna:
        expected = DataArray(expected)
    else:
        expected = DataArray(np.nan)

    result = da.weighted(weights).mean(skipna=skipna)

    assert_equal(expected, result)


def test_weighted_mean_bool():
    # https://github.com/pydata/xarray/issues/4074
    da = DataArray([1, 1])
    weights = DataArray([True, True])
    expected = DataArray(1)

    result = da.weighted(weights).mean()

    assert_equal(expected, result)


def expected_weighted(da, weights, dim, skipna, operation):
    """
    Generate expected result using ``*`` and ``sum``. This is checked against
    the result of da.weighted which uses ``dot``
    """

    weighted_sum = (da * weights).sum(dim=dim, skipna=skipna)

    if operation == "sum":
        return weighted_sum

    masked_weights = weights.where(da.notnull())
    sum_of_weights = masked_weights.sum(dim=dim, skipna=True)
    valid_weights = sum_of_weights != 0
    sum_of_weights = sum_of_weights.where(valid_weights)

    if operation == "sum_of_weights":
        return sum_of_weights

    weighted_mean = weighted_sum / sum_of_weights

    if operation == "mean":
        return weighted_mean


@pytest.mark.parametrize("dim", ("a", "b", "c", ("a", "b"), ("a", "b", "c"), None))
@pytest.mark.parametrize("operation", ("sum_of_weights", "sum", "mean"))
@pytest.mark.parametrize("add_nans", (True, False))
@pytest.mark.parametrize("skipna", (None, True, False))
@pytest.mark.parametrize("as_dataset", (True, False))
def test_weighted_operations_3D(dim, operation, add_nans, skipna, as_dataset):

    dims = ("a", "b", "c")
    coords = dict(a=[0, 1, 2, 3], b=[0, 1, 2, 3], c=[0, 1, 2, 3])

    weights = DataArray(np.random.randn(4, 4, 4), dims=dims, coords=coords)

    data = np.random.randn(4, 4, 4)

    # add approximately 25 % NaNs (https://stackoverflow.com/a/32182680/3010700)
    if add_nans:
        c = int(data.size * 0.25)
        data.ravel()[np.random.choice(data.size, c, replace=False)] = np.NaN

    data = DataArray(data, dims=dims, coords=coords)

    if as_dataset:
        data = data.to_dataset(name="data")

    if operation == "sum_of_weights":
        result = data.weighted(weights).sum_of_weights(dim)
    else:
        result = getattr(data.weighted(weights), operation)(dim, skipna=skipna)

    expected = expected_weighted(data, weights, dim, skipna, operation)

    assert_allclose(expected, result)


@pytest.mark.parametrize("operation", ("sum_of_weights", "sum", "mean"))
@pytest.mark.parametrize("as_dataset", (True, False))
def test_weighted_operations_nonequal_coords(operation, as_dataset):

    weights = DataArray(np.random.randn(4), dims=("a",), coords=dict(a=[0, 1, 2, 3]))
    data = DataArray(np.random.randn(4), dims=("a",), coords=dict(a=[1, 2, 3, 4]))

    if as_dataset:
        data = data.to_dataset(name="data")

    expected = expected_weighted(
        data, weights, dim="a", skipna=None, operation=operation
    )
    result = getattr(data.weighted(weights), operation)(dim="a")

    assert_allclose(expected, result)


@pytest.mark.parametrize("dim", ("dim_0", None))
@pytest.mark.parametrize("shape_data", ((4,), (4, 4), (4, 4, 4)))
@pytest.mark.parametrize("shape_weights", ((4,), (4, 4), (4, 4, 4)))
@pytest.mark.parametrize("operation", ("sum_of_weights", "sum", "mean"))
@pytest.mark.parametrize("add_nans", (True, False))
@pytest.mark.parametrize("skipna", (None, True, False))
@pytest.mark.parametrize("as_dataset", (True, False))
def test_weighted_operations_different_shapes(
    dim, shape_data, shape_weights, operation, add_nans, skipna, as_dataset
):

    weights = DataArray(np.random.randn(*shape_weights))

    data = np.random.randn(*shape_data)

    # add approximately 25 % NaNs
    if add_nans:
        c = int(data.size * 0.25)
        data.ravel()[np.random.choice(data.size, c, replace=False)] = np.NaN

    data = DataArray(data)

    if as_dataset:
        data = data.to_dataset(name="data")

    if operation == "sum_of_weights":
        result = getattr(data.weighted(weights), operation)(dim)
    else:
        result = getattr(data.weighted(weights), operation)(dim, skipna=skipna)

    expected = expected_weighted(data, weights, dim, skipna, operation)

    assert_allclose(expected, result)


@pytest.mark.parametrize("operation", ("sum_of_weights", "sum", "mean"))
@pytest.mark.parametrize("as_dataset", (True, False))
@pytest.mark.parametrize("keep_attrs", (True, False, None))
def test_weighted_operations_keep_attr(operation, as_dataset, keep_attrs):

    weights = DataArray(np.random.randn(2, 2), attrs=dict(attr="weights"))
    data = DataArray(np.random.randn(2, 2))

    if as_dataset:
        data = data.to_dataset(name="data")

    data.attrs = dict(attr="weights")

    result = getattr(data.weighted(weights), operation)(keep_attrs=True)

    if operation == "sum_of_weights":
        assert weights.attrs == result.attrs
    else:
        assert data.attrs == result.attrs

    result = getattr(data.weighted(weights), operation)(keep_attrs=None)
    assert not result.attrs

    result = getattr(data.weighted(weights), operation)(keep_attrs=False)
    assert not result.attrs


@pytest.mark.xfail(reason="xr.Dataset.map does not copy attrs of DataArrays GH: 3595")
@pytest.mark.parametrize("operation", ("sum", "mean"))
def test_weighted_operations_keep_attr_da_in_ds(operation):
    """
    Performs a weighted operation on a dataset and keeps the attributes of the original data.
    
    This function applies a specified weighted operation on a dataset and ensures that the attributes of the original data are preserved.
    
    Parameters:
    operation (str): The name of the operation to perform on the weighted data. This should be a method name available in the `weighted` object.
    
    Returns:
    xarray.Dataset: A new dataset with the result of the weighted operation applied, retaining the attributes of the original data.
    
    Example
    """

    # GH #3595

    weights = DataArray(np.random.randn(2, 2))
    data = DataArray(np.random.randn(2, 2), attrs=dict(attr="data"))
    data = data.to_dataset(name="a")

    result = getattr(data.weighted(weights), operation)(keep_attrs=True)

    assert data.a.attrs == result.a.attrs
