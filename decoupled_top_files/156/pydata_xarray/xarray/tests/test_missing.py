import itertools

import numpy as np
import pandas as pd
import pytest

import xarray as xr
from xarray.core.missing import NumpyInterpolator, ScipyInterpolator, SplineInterpolator
from xarray.core.pycompat import dask_array_type
from xarray.tests import (
    assert_array_equal,
    assert_equal,
    raises_regex,
    requires_bottleneck,
    requires_dask,
    requires_scipy,
)


@pytest.fixture
def da():
    return xr.DataArray([0, np.nan, 1, 2, np.nan, 3, 4, 5, np.nan, 6, 7], dims="time")


@pytest.fixture
def ds():
    """
    Create an xarray Dataset with two DataArrays.
    
    This function initializes an xarray Dataset and populates it with two
    DataArrays: 'var1' and 'var2'. The 'var1' DataArray contains time series data
    with some missing values (NaNs), while 'var2' contains x-axis data with
    missing values as well.
    
    Parameters:
    None
    
    Returns:
    ds (xr.Dataset): An xarray Dataset containing two DataArrays:
    """

    ds = xr.Dataset()
    ds["var1"] = xr.DataArray(
        [0, np.nan, 1, 2, np.nan, 3, 4, 5, np.nan, 6, 7], dims="time"
    )
    ds["var2"] = xr.DataArray(
        [10, np.nan, 11, 12, np.nan, 13, 14, 15, np.nan, 16, 17], dims="x"
    )
    return ds


def make_interpolate_example_data(shape, frac_nan, seed=12345, non_uniform=False):
    """
    Generate example interpolated data.
    
    This function creates an example dataset with missing values and returns it
    as both an xarray DataArray and a pandas DataFrame. The dataset is generated
    using random normal values and can be customized with the fraction of missing
    values and whether the time coordinates are uniformly or non-uniformly spaced.
    
    Parameters
    ----------
    shape : tuple
    Shape of the generated data (number of time points, number of spatial points).
    frac_nan : float
    """

    rs = np.random.RandomState(seed)
    vals = rs.normal(size=shape)
    if frac_nan == 1:
        vals[:] = np.nan
    elif frac_nan == 0:
        pass
    else:
        n_missing = int(vals.size * frac_nan)

        ys = np.arange(shape[0])
        xs = np.arange(shape[1])
        if n_missing:
            np.random.shuffle(ys)
            ys = ys[:n_missing]

            np.random.shuffle(xs)
            xs = xs[:n_missing]

            vals[ys, xs] = np.nan

    if non_uniform:
        # construct a datetime index that has irregular spacing
        deltas = pd.TimedeltaIndex(unit="d", data=rs.normal(size=shape[0], scale=10))
        coords = {"time": (pd.Timestamp("2000-01-01") + deltas).sort_values()}
    else:
        coords = {"time": pd.date_range("2000-01-01", freq="D", periods=shape[0])}
    da = xr.DataArray(vals, dims=("time", "x"), coords=coords)
    df = da.to_pandas()

    return da, df


@requires_scipy
def test_interpolate_pd_compat():
    """
    Interpolates missing values in a DataArray along a specified dimension using various methods.
    
    This function tests the interpolation of missing values in a DataArray (`da`) by comparing the results with those obtained from Pandas' `interpolate` method applied to a DataFrame (`df`). The interpolation is performed along a specified dimension (`dim`), and different methods such as 'linear', 'nearest', 'zero', 'slinear', 'quadratic', and 'cubic' can be used. The
    """

    shapes = [(8, 8), (1, 20), (20, 1), (100, 100)]
    frac_nans = [0, 0.5, 1]
    methods = ["linear", "nearest", "zero", "slinear", "quadratic", "cubic"]

    for (shape, frac_nan, method) in itertools.product(shapes, frac_nans, methods):

        da, df = make_interpolate_example_data(shape, frac_nan)

        for dim in ["time", "x"]:
            actual = da.interpolate_na(method=method, dim=dim, fill_value=np.nan)
            expected = df.interpolate(
                method=method, axis=da.get_axis_num(dim), fill_value=(np.nan, np.nan)
            )
            # Note, Pandas does some odd things with the left/right fill_value
            # for the linear methods. This next line inforces the xarray
            # fill_value convention on the pandas output. Therefore, this test
            # only checks that interpolated values are the same (not nans)
            expected.values[pd.isnull(actual.values)] = np.nan

            np.testing.assert_allclose(actual.values, expected.values)


@requires_scipy
@pytest.mark.parametrize("method", ["barycentric", "krog", "pchip", "spline", "akima"])
def test_scipy_methods_function(method):
    """
    Interpolates missing values along the 'time' dimension using the specified method.
    
    Parameters:
    method (str): The interpolation method to use. Supported methods include 'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', etc.
    
    Returns:
    xarray.DataArray: The interpolated DataArray with missing values filled.
    
    Notes:
    - The function uses `pandas` for interpolation, which may behave differently for certain methods.
    - The
    """

    # Note: Pandas does some wacky things with these methods and the full
    # integration tests wont work.
    da, _ = make_interpolate_example_data((25, 25), 0.4, non_uniform=True)
    actual = da.interpolate_na(method=method, dim="time")
    assert (da.count("time") <= actual.count("time")).all()


@requires_scipy
def test_interpolate_pd_compat_non_uniform_index():
    """
    Interpolates missing values in a DataArray along a specified dimension using linear interpolation.
    
    This function tests the `interpolate_na` method of a DataArray against the corresponding functionality in Pandas.
    It iterates over different shapes, fractions of NaNs, and interpolation methods, generating example data for each case.
    The function then compares the interpolated results from xarray and Pandas to ensure they match.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    """

    shapes = [(8, 8), (1, 20), (20, 1), (100, 100)]
    frac_nans = [0, 0.5, 1]
    methods = ["time", "index", "values"]

    for (shape, frac_nan, method) in itertools.product(shapes, frac_nans, methods):

        da, df = make_interpolate_example_data(shape, frac_nan, non_uniform=True)
        for dim in ["time", "x"]:
            if method == "time" and dim != "time":
                continue
            actual = da.interpolate_na(
                method="linear", dim=dim, use_coordinate=True, fill_value=np.nan
            )
            expected = df.interpolate(
                method=method, axis=da.get_axis_num(dim), fill_value=np.nan
            )

            # Note, Pandas does some odd things with the left/right fill_value
            # for the linear methods. This next line inforces the xarray
            # fill_value convention on the pandas output. Therefore, this test
            # only checks that interpolated values are the same (not nans)
            expected.values[pd.isnull(actual.values)] = np.nan

            np.testing.assert_allclose(actual.values, expected.values)


@requires_scipy
def test_interpolate_pd_compat_polynomial():
    """
    Interpolates missing values in a DataArray using polynomial interpolation.
    
    This function tests the `interpolate_na` method with polynomial interpolation on various shapes of DataArray and DataFrame objects. It checks the compatibility between xarray and pandas for different fractions of NaN values and polynomial orders.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `make_interpolate_example_data`: Generates example data for testing.
    - `interpolate_na`: Interpolates missing values in
    """

    shapes = [(8, 8), (1, 20), (20, 1), (100, 100)]
    frac_nans = [0, 0.5, 1]
    orders = [1, 2, 3]

    for (shape, frac_nan, order) in itertools.product(shapes, frac_nans, orders):

        da, df = make_interpolate_example_data(shape, frac_nan)

        for dim in ["time", "x"]:
            actual = da.interpolate_na(
                method="polynomial", order=order, dim=dim, use_coordinate=False
            )
            expected = df.interpolate(
                method="polynomial", order=order, axis=da.get_axis_num(dim)
            )
            np.testing.assert_allclose(actual.values, expected.values)


@requires_scipy
def test_interpolate_unsorted_index_raises():
    """
    Interpolates missing values in a DataArray along the 'x' dimension using index-based interpolation. Raises a ValueError if the index is not monotonically increasing.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the index is not monotonically increasing.
    
    Example:
    Given a DataArray `expected` with values [1, 2, 3] at coordinates [2, 1, 3],
    attempting to interpolate missing values
    """

    vals = np.array([1, 2, 3], dtype=np.float64)
    expected = xr.DataArray(vals, dims="x", coords={"x": [2, 1, 3]})
    with raises_regex(ValueError, "Index must be monotonicly increasing"):
        expected.interpolate_na(dim="x", method="index")


def test_interpolate_no_dim_raises():
    """
    Interpolate missing values in a DataArray along the 'x' dimension using linear method.
    
    Parameters:
    -----------
    da : xarray.DataArray
    Input DataArray containing missing (NaN) values along the 'x' dimension.
    
    Raises:
    -------
    NotImplementedError
    If no dimension ('dim') is specified, indicating that the interpolation method requires a specific dimension to operate on.
    
    Notes:
    ------
    This function interpolates missing values in the input DataArray `da
    """

    da = xr.DataArray(np.array([1, 2, np.nan, 5], dtype=np.float64), dims="x")
    with raises_regex(NotImplementedError, "dim is a required argument"):
        da.interpolate_na(method="linear")


def test_interpolate_invalid_interpolator_raises():
    """
    Interpolate missing values in a DataArray along a specified dimension using an invalid interpolation method.
    
    This function attempts to interpolate missing (NaN) values in a one-dimensional
    DataArray using an invalid interpolation method, which should raise a ValueError.
    
    Parameters:
    -----------
    da : xarray.DataArray
    The input DataArray containing missing values.
    
    Returns:
    --------
    None
    
    Raises:
    -------
    ValueError
    If an invalid interpolation method is provided, a ValueError is
    """

    da = xr.DataArray(np.array([1, 2, np.nan, 5], dtype=np.float64), dims="x")
    with raises_regex(ValueError, "not a valid"):
        da.interpolate_na(dim="x", method="foo")


def test_interpolate_multiindex_raises():
    """
    Interpolates missing values in a multi-indexed DataArray along the specified dimension.
    
    This function takes a multi-indexed `DataArray` and interpolates missing values (NaNs) along the specified dimension using linear interpolation. If the index cannot be cast to float64, a TypeError is raised.
    
    Parameters:
    -----------
    das : xarray.DataArray
    The multi-indexed DataArray containing missing values to be interpolated.
    
    Raises:
    -------
    TypeError
    If
    """

    data = np.random.randn(2, 3)
    data[1, 1] = np.nan
    da = xr.DataArray(data, coords=[("x", ["a", "b"]), ("y", [0, 1, 2])])
    das = da.stack(z=("x", "y"))
    with raises_regex(TypeError, "Index must be castable to float64"):
        das.interpolate_na(dim="z")


def test_interpolate_2d_coord_raises():
    """
    Interpolates missing values (NaNs) along a specified dimension in a 2D DataArray using linear interpolation.
    
    Parameters:
    -----------
    da : xarray.DataArray
    The 2D DataArray containing the data to be interpolated.
    
    Raises:
    -------
    ValueError
    If the specified dimension for interpolation is not 1D.
    
    Notes:
    ------
    - The function checks if the specified coordinate for interpolation is 1D.
    - It raises a
    """

    coords = {
        "x": xr.Variable(("a", "b"), np.arange(6).reshape(2, 3)),
        "y": xr.Variable(("a", "b"), np.arange(6).reshape(2, 3)) * 2,
    }

    data = np.random.randn(2, 3)
    data[1, 1] = np.nan
    da = xr.DataArray(data, dims=("a", "b"), coords=coords)
    with raises_regex(ValueError, "interpolation must be 1D"):
        da.interpolate_na(dim="a", use_coordinate="x")


@requires_scipy
def test_interpolate_kwargs():
    """
    Interpolate missing values in a DataArray along a specified dimension.
    
    This function interpolates missing (NaN) values in a `xarray.DataArray`
    object along the given dimension using different fill values.
    
    Parameters:
    da (xarray.DataArray): The input DataArray containing missing values.
    dim (str): The dimension along which to interpolate missing values.
    fill_value (float or "extrapolate"): The value to use for filling
    missing values during interpolation. If
    """

    da = xr.DataArray(np.array([4, 5, np.nan], dtype=np.float64), dims="x")
    expected = xr.DataArray(np.array([4, 5, 6], dtype=np.float64), dims="x")
    actual = da.interpolate_na(dim="x", fill_value="extrapolate")
    assert_equal(actual, expected)

    expected = xr.DataArray(np.array([4, 5, -999], dtype=np.float64), dims="x")
    actual = da.interpolate_na(dim="x", fill_value=-999)
    assert_equal(actual, expected)


def test_interpolate():
    """
    Interpolates missing values in a DataArray along the 'x' dimension.
    
    This function takes a DataArray with missing (NaN) values and interpolates them using linear interpolation. The input DataArray must have the dimension 'x'.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    Given a DataArray `missing` with some missing values, this function will return an interpolated DataArray `actual` with no missing values.
    
    ```python
    import numpy as
    """


    vals = np.array([1, 2, 3, 4, 5, 6], dtype=np.float64)
    expected = xr.DataArray(vals, dims="x")
    mvals = vals.copy()
    mvals[2] = np.nan
    missing = xr.DataArray(mvals, dims="x")

    actual = missing.interpolate_na(dim="x")

    assert_equal(actual, expected)


def test_interpolate_nonans():
    """
    Interpolates missing values (NaNs) along the 'x' dimension of an xarray DataArray.
    
    This function takes an xarray DataArray with float64 data type and interpolates
    missing values (NaNs) along the specified dimension ('x'). The resulting DataArray
    should be identical to the original if no NaNs are present.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> vals = np.array([1, 2
    """


    vals = np.array([1, 2, 3, 4, 5, 6], dtype=np.float64)
    expected = xr.DataArray(vals, dims="x")
    actual = expected.interpolate_na(dim="x")
    assert_equal(actual, expected)


@requires_scipy
def test_interpolate_allnans():
    """
    Interpolates all NaN values along the 'x' dimension of a DataArray.
    
    This function creates a DataArray filled with NaN values and then interpolates
    these NaN values along the 'x' dimension using the `interpolate_na` method.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The input DataArray is filled with NaN values.
    - The interpolation is performed along the 'x' dimension.
    - The resulting DataArray after interpolation
    """

    vals = np.full(6, np.nan, dtype=np.float64)
    expected = xr.DataArray(vals, dims="x")
    actual = expected.interpolate_na(dim="x")

    assert_equal(actual, expected)


@requires_bottleneck
def test_interpolate_limits():
    """
    Interpolates missing values (NaNs) in a DataArray along the 'x' dimension using linear interpolation.
    
    Parameters:
    -----------
    da : xarray.DataArray
    The input DataArray containing NaNs to be interpolated.
    
    limit : int or None, optional
    Maximum number of consecutive NaNs to interpolate. If None, all NaNs are interpolated. Default is None.
    
    Returns:
    --------
    xarray.DataArray
    The interpolated DataArray with NaNs
    """

    da = xr.DataArray(
        np.array([1, 2, np.nan, np.nan, np.nan, 6], dtype=np.float64), dims="x"
    )

    actual = da.interpolate_na(dim="x", limit=None)
    assert actual.isnull().sum() == 0

    actual = da.interpolate_na(dim="x", limit=2)
    expected = xr.DataArray(
        np.array([1, 2, 3, 4, np.nan, 6], dtype=np.float64), dims="x"
    )

    assert_equal(actual, expected)


@requires_scipy
def test_interpolate_methods():
    """
    Interpolates missing values in a DataArray along the 'x' dimension using various methods.
    
    This function tests the interpolation of missing values (NaNs) in a one-dimensional
    DataArray along the 'x' dimension using different interpolation methods. It checks
    that the number of NaNs in the interpolated DataArray is reduced or limited according
    to the specified method and limit parameter.
    
    Parameters:
    None
    
    Returns:
    None
    
    Methods tested:
    - linear
    """

    for method in ["linear", "nearest", "zero", "slinear", "quadratic", "cubic"]:
        kwargs = {}
        da = xr.DataArray(
            np.array([0, 1, 2, np.nan, np.nan, np.nan, 6, 7, 8], dtype=np.float64),
            dims="x",
        )
        actual = da.interpolate_na("x", method=method, **kwargs)
        assert actual.isnull().sum() == 0

        actual = da.interpolate_na("x", method=method, limit=2, **kwargs)
        assert actual.isnull().sum() == 1


@requires_scipy
def test_interpolators():
    """
    Test various interpolation methods using different interpolator classes.
    
    This function evaluates the specified interpolation methods on given data points
    and checks if the output is valid (i.e., not containing any NaN or infinity values).
    
    Parameters:
    None
    
    Returns:
    None
    
    Methods:
    - `NumpyInterpolator`: Interpolator class from numpy library.
    - `ScipyInterpolator`: Interpolator class from scipy library.
    - `SplineInterpolator`: Custom spline interpolator class.
    """

    for method, interpolator in [
        ("linear", NumpyInterpolator),
        ("linear", ScipyInterpolator),
        ("spline", SplineInterpolator),
    ]:
        xi = np.array([-1, 0, 1, 2, 5], dtype=np.float64)
        yi = np.array([-10, 0, 10, 20, 50], dtype=np.float64)
        x = np.array([3, 4], dtype=np.float64)

        f = interpolator(xi, yi, method=method)
        out = f(x)
        assert pd.isnull(out).sum() == 0


def test_interpolate_use_coordinate():
    """
    Interpolates missing values in a DataArray along the specified dimension.
    
    This function interpolates missing (NaN) values in a DataArray `da` along the
    dimension 'x'. The interpolation can be performed using either the default index
    or a specified coordinate variable.
    
    Parameters:
    -----------
    da : xarray.DataArray
    The input DataArray containing missing values to be interpolated.
    dim : str
    The dimension along which to interpolate missing values.
    use
    """

    xc = xr.Variable("x", [100, 200, 300, 400, 500, 600])
    da = xr.DataArray(
        np.array([1, 2, np.nan, np.nan, np.nan, 6], dtype=np.float64),
        dims="x",
        coords={"xc": xc},
    )

    # use_coordinate == False is same as using the default index
    actual = da.interpolate_na(dim="x", use_coordinate=False)
    expected = da.interpolate_na(dim="x")
    assert_equal(actual, expected)

    # possible to specify non index coordinate
    actual = da.interpolate_na(dim="x", use_coordinate="xc")
    expected = da.interpolate_na(dim="x")
    assert_equal(actual, expected)

    # possible to specify index coordinate by name
    actual = da.interpolate_na(dim="x", use_coordinate="x")
    expected = da.interpolate_na(dim="x")
    assert_equal(actual, expected)


@requires_dask
def test_interpolate_dask():
    """
    Interpolates missing values in a Dask array along the 'time' dimension.
    
    This function takes a Dask array `da` and interpolates missing values along the 'time' dimension using Dask's lazy evaluation capabilities. It supports specifying a `limit` parameter to control the maximum number of consecutive missing values to interpolate.
    
    Parameters:
    da (Dask Array): Input Dask array containing time series data with potential missing values.
    
    Returns:
    Dask Array: Interpol
    """

    da, _ = make_interpolate_example_data((40, 40), 0.5)
    da = da.chunk({"x": 5})
    actual = da.interpolate_na("time")
    expected = da.load().interpolate_na("time")
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual.compute(), expected)

    # with limit
    da = da.chunk({"x": 5})
    actual = da.interpolate_na("time", limit=3)
    expected = da.load().interpolate_na("time", limit=3)
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual, expected)


@requires_dask
def test_interpolate_dask_raises_for_invalid_chunk_dim():
    """
    Interpolates missing values in a Dask array along the 'time' dimension using linear interpolation.
    
    This function raises a ValueError if the Dask array is chunked along the 'time' dimension.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Raises:
    -------
    ValueError
    If the Dask array is chunked along the 'time' dimension.
    
    Notes:
    ------
    - The function uses `make_interpolate_example_data`
    """

    da, _ = make_interpolate_example_data((40, 40), 0.5)
    da = da.chunk({"time": 5})
    with raises_regex(ValueError, "dask='parallelized' consists of multiple"):
        da.interpolate_na("time")


@requires_bottleneck
def test_ffill():
    """
    Fill missing values along the specified dimension using forward filling.
    
    Parameters:
    -----------
    da : xarray.DataArray
    The input DataArray containing missing (NaN) values.
    
    Returns:
    --------
    xarray.DataArray
    The DataArray with missing values filled using forward filling.
    
    Example:
    --------
    >>> import numpy as np
    >>> import xarray as xr
    >>> da = xr.DataArray(np.array([4, 5, np.nan], dtype=np
    """

    da = xr.DataArray(np.array([4, 5, np.nan], dtype=np.float64), dims="x")
    expected = xr.DataArray(np.array([4, 5, 5], dtype=np.float64), dims="x")
    actual = da.ffill("x")
    assert_equal(actual, expected)


@requires_bottleneck
@requires_dask
def test_ffill_dask():
    """
    Fill NaN values forward along the 'time' dimension using Dask for large datasets.
    
    This function takes a Dask array `da` with dimensions including 'time', and fills
    NaN values forward along the 'time' dimension. The function supports specifying a
    `limit` parameter to limit the number of consecutive NaN values to fill.
    
    Parameters:
    - da (Dask Array): Input Dask array with dimensions including 'time'.
    
    Returns:
    - Dask
    """

    da, _ = make_interpolate_example_data((40, 40), 0.5)
    da = da.chunk({"x": 5})
    actual = da.ffill("time")
    expected = da.load().ffill("time")
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual, expected)

    # with limit
    da = da.chunk({"x": 5})
    actual = da.ffill("time", limit=3)
    expected = da.load().ffill("time", limit=3)
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual, expected)


@requires_bottleneck
@requires_dask
def test_bfill_dask():
    """
    Fill NaN values in a Dask array along the 'time' dimension using backward fill method.
    
    This function takes a Dask array `da` and fills NaN values by propagating the last valid observation backward along the 'time' dimension. The function supports both without and with a specified limit on the number of consecutive NaNs to fill.
    
    Parameters:
    da (Dask Array): Input Dask array containing time series data.
    
    Returns:
    Dask Array: Output Dask array
    """

    da, _ = make_interpolate_example_data((40, 40), 0.5)
    da = da.chunk({"x": 5})
    actual = da.bfill("time")
    expected = da.load().bfill("time")
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual, expected)

    # with limit
    da = da.chunk({"x": 5})
    actual = da.bfill("time", limit=3)
    expected = da.load().bfill("time", limit=3)
    assert isinstance(actual.data, dask_array_type)
    assert_equal(actual, expected)


@requires_bottleneck
def test_ffill_bfill_nonans():
    """
    Fill missing values along the specified dimension using forward and backward fill methods.
    
    This function takes an xarray DataArray with float64 values and performs
    forward filling (ffill) and backward filling (bfill) along the 'x' dimension.
    The input array remains unchanged after these operations, as there are no
    missing values (NaNs) present.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    Given an input array:
    <1
    """


    vals = np.array([1, 2, 3, 4, 5, 6], dtype=np.float64)
    expected = xr.DataArray(vals, dims="x")

    actual = expected.ffill(dim="x")
    assert_equal(actual, expected)

    actual = expected.bfill(dim="x")
    assert_equal(actual, expected)


@requires_bottleneck
def test_ffill_bfill_allnans():
    """
    Fill NaN values along the 'x' dimension using forward and backward fill methods.
    
    This function tests the forward fill (ffill) and backward fill (bfill) methods
    on a DataArray filled with NaN values. The input is a 1-dimensional DataArray
    with 6 NaN entries. Both ffill and bfill methods are applied to this array,
    and the result is compared to the original array, expecting no changes since
    all values are NaN.
    
    Parameters
    """


    vals = np.full(6, np.nan, dtype=np.float64)
    expected = xr.DataArray(vals, dims="x")

    actual = expected.ffill(dim="x")
    assert_equal(actual, expected)

    actual = expected.bfill(dim="x")
    assert_equal(actual, expected)


@requires_bottleneck
def test_ffill_functions(da):
    result = da.ffill("time")
    assert result.isnull().sum() == 0


@requires_bottleneck
def test_ffill_limit():
    """
    Fill NaN values in a DataArray along the 'time' dimension using forward filling method. The function supports specifying a limit on the number of consecutive NaNs to fill.
    
    Parameters:
    da (xarray.DataArray): Input DataArray containing NaN values.
    
    Returns:
    xarray.DataArray: DataArray with NaN values filled using forward filling method, optionally limited by the specified number of consecutive NaNs.
    
    Examples:
    >>> da = xr.DataArray([0, np.nan, np
    """

    da = xr.DataArray(
        [0, np.nan, np.nan, np.nan, np.nan, 3, 4, 5, np.nan, 6, 7], dims="time"
    )
    result = da.ffill("time")
    expected = xr.DataArray([0, 0, 0, 0, 0, 3, 4, 5, 5, 6, 7], dims="time")
    assert_array_equal(result, expected)

    result = da.ffill("time", limit=1)
    expected = xr.DataArray(
        [0, 0, np.nan, np.nan, np.nan, 3, 4, 5, 5, 6, 7], dims="time"
    )
    assert_array_equal(result, expected)


def test_interpolate_dataset(ds):
    """
    Interpolates missing values in a dataset along the 'time' dimension.
    
    Parameters:
    ds (xarray.Dataset): Input dataset containing variables with potential missing values.
    
    Returns:
    xarray.Dataset: Interpolated dataset with missing values filled along the 'time' dimension.
    
    Notes:
    - The function interpolates missing values in the variable 'var1'.
    - The variable 'var2' remains unchanged.
    - The interpolated dataset is returned with the same dimensions as the input
    """

    actual = ds.interpolate_na(dim="time")
    # no missing values in var1
    assert actual["var1"].count("time") == actual.dims["time"]

    # var2 should be the same as it was
    assert_array_equal(actual["var2"], ds["var2"])


@requires_bottleneck
def test_ffill_dataset(ds):
    ds.ffill(dim="time")


@requires_bottleneck
def test_bfill_dataset(ds):
    ds.ffill(dim="time")
