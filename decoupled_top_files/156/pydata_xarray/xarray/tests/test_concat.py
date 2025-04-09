from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from xarray import DataArray, Dataset, Variable, concat
from xarray.core import dtypes, merge

from . import (
    InaccessibleArray,
    assert_array_equal,
    assert_equal,
    assert_identical,
    raises_regex,
    requires_dask,
)
from .test_dataset import create_test_data


def test_concat_compat():
    """
    Concatenate multiple xarray Datasets along a new dimension.
    
    Parameters:
    -----------
    datasets : list of xarray.Dataset
    The datasets to be concatenated.
    dim : str
    The name of the new dimension along which to concatenate.
    data_vars : str or list of str
    Specifies how to handle data variables during concatenation.
    Options are 'minimal', 'different', 'all', or a list of variable names.
    compat : str
    Compatibility check mode
    """

    ds1 = Dataset(
        {
            "has_x_y": (("y", "x"), [[1, 2]]),
            "has_x": ("x", [1, 2]),
            "no_x_y": ("z", [1, 2]),
        },
        coords={"x": [0, 1], "y": [0], "z": [-1, -2]},
    )
    ds2 = Dataset(
        {
            "has_x_y": (("y", "x"), [[3, 4]]),
            "has_x": ("x", [1, 2]),
            "no_x_y": (("q", "z"), [[1, 2]]),
        },
        coords={"x": [0, 1], "y": [1], "z": [-1, -2], "q": [0]},
    )

    result = concat([ds1, ds2], dim="y", data_vars="minimal", compat="broadcast_equals")
    assert_equal(ds2.no_x_y, result.no_x_y.transpose())

    for var in ["has_x", "no_x_y"]:
        assert "y" not in result[var]

    with raises_regex(ValueError, "coordinates in some datasets but not others"):
        concat([ds1, ds2], dim="q")
    with raises_regex(ValueError, "'q' is not present in all datasets"):
        concat([ds2, ds1], dim="q")


class TestConcatDataset:
    @pytest.fixture
    def data(self):
        return create_test_data().drop_dims("dim3")

    def rectify_dim_order(self, data, dataset):
        """
        Rectifies the dimension order of a dataset by transposing its variables to match the order of dimensions in the given data.
        
        Args:
        data (xarray.Dataset): The reference dataset containing the desired dimension order.
        dataset (xarray.Dataset): The target dataset whose variables' dimensions will be transposed.
        
        Returns:
        xarray.Dataset: A new dataset with all variable dimensions transposed into the order found in `data`.
        """

        # return a new dataset with all variable dimensions transposed into
        # the order in which they are found in `data`
        return Dataset(
            {k: v.transpose(*data[k].dims) for k, v in dataset.data_vars.items()},
            dataset.coords,
            attrs=dataset.attrs,
        )

    @pytest.mark.parametrize("coords", ["different", "minimal"])
    @pytest.mark.parametrize("dim", ["dim1", "dim2"])
    def test_concat_simple(self, data, dim, coords):
        datasets = [g for _, g in data.groupby(dim, squeeze=False)]
        assert_identical(data, concat(datasets, dim, coords=coords))

    def test_concat_2(self, data):
        """
        Concatenates multiple groups of data along a specified dimension while preserving other coordinates.
        
        Parameters:
        -----------
        data : xarray.Dataset
        The input dataset containing multiple groups to be concatenated.
        
        Returns:
        --------
        xarray.Dataset
        The concatenated dataset with the same dimensions and coordinates as the input, except for the specified dimension.
        
        Important Functions:
        --------------------
        - `groupby`: Splits the dataset into groups based on the specified dimension.
        - `concat`:
        """

        dim = "dim2"
        datasets = [g for _, g in data.groupby(dim, squeeze=True)]
        concat_over = [k for k, v in data.coords.items() if dim in v.dims and k != dim]
        actual = concat(datasets, data[dim], coords=concat_over)
        assert_identical(data, self.rectify_dim_order(data, actual))

    @pytest.mark.parametrize("coords", ["different", "minimal", "all"])
    @pytest.mark.parametrize("dim", ["dim1", "dim2"])
    def test_concat_coords_kwarg(self, data, dim, coords):
        """
        Concatenate multiple grouped datasets along a specified dimension using the `concat` function. This function ensures that the coordinates are handled correctly based on the provided `coords` keyword.
        
        Parameters:
        -----------
        data : xarray.Dataset
        The original dataset to be grouped and concatenated.
        dim : str
        The dimension along which to group and concatenate the datasets.
        coords : str
        Specifies how to handle coordinates during concatenation. Can be either 'minimal' or 'all'.
        """

        data = data.copy(deep=True)
        # make sure the coords argument behaves as expected
        data.coords["extra"] = ("dim4", np.arange(3))
        datasets = [g for _, g in data.groupby(dim, squeeze=True)]

        actual = concat(datasets, data[dim], coords=coords)
        if coords == "all":
            expected = np.array([data["extra"].values for _ in range(data.dims[dim])])
            assert_array_equal(actual["extra"].values, expected)

        else:
            assert_equal(data["extra"], actual["extra"])

    def test_concat(self, data):
        """
        Concatenate multiple xarray DataArray or Dataset objects along a new dimension 'dim1'. The function takes an input `data` and splits it into three parts based on the 'dim1' dimension using slicing. These slices are then concatenated back together along the 'dim1' dimension to verify if the original data is recovered.
        
        Parameters:
        -----------
        data : xarray.DataArray or xarray.Dataset
        The input data to be split and concatenated.
        
        Returns:
        --------
        """

        split_data = [
            data.isel(dim1=slice(3)),
            data.isel(dim1=3),
            data.isel(dim1=slice(4, None)),
        ]
        assert_identical(data, concat(split_data, "dim1"))

    def test_concat_dim_precedence(self, data):
        """
        Verify that the `dim` argument takes precedence over concatenating dataset variables of the same name. The function groups the input data by 'dim1', doubles the values of 'dim1', renames the dimension, and then concatenates the resulting datasets along the specified dimension.
        
        Parameters:
        -----------
        data : xarray.Dataset
        The input dataset containing variables to be concatenated.
        
        Returns:
        --------
        None
        
        Important Functions:
        - `groupby`: Groups the dataset by
        """

        # verify that the dim argument takes precedence over
        # concatenating dataset variables of the same name
        dim = (2 * data["dim1"]).rename("dim1")
        datasets = [g for _, g in data.groupby("dim1", squeeze=False)]
        expected = data.copy()
        expected["dim1"] = dim
        assert_identical(expected, concat(datasets, dim))

    def test_concat_data_vars(self):
        """
        Concatenate multiple xarray datasets or data arrays along a new dimension.
        
        Parameters:
        -----------
        objs : list of xarray.Dataset or xarray.DataArray
        The datasets or data arrays to be concatenated.
        dim : str
        The name of the new dimension along which to concatenate.
        data_vars : str or list of str, optional
        Specifies how to handle data variables:
        - 'minimal': only variables that appear in all objects are concatenated.
        - 'different
        """

        data = Dataset({"foo": ("x", np.random.randn(10))})
        objs = [data.isel(x=slice(5)), data.isel(x=slice(5, None))]
        for data_vars in ["minimal", "different", "all", [], ["foo"]]:
            actual = concat(objs, dim="x", data_vars=data_vars)
            assert_identical(data, actual)

    def test_concat_coords(self):
        """
        Concatenate multiple xarray datasets or dataarrays along a new dimension.
        
        Parameters:
        -----------
        objs : list of xarray.Dataset or xarray.DataArray
        The datasets or dataarrays to be concatenated.
        dim : str
        The name of the new dimension along which to concatenate the objects.
        coords : str or list of str, optional
        Specifies how to handle coordinates:
        - 'different': Use different coordinates from each object.
        - 'all': Use all
        """

        data = Dataset({"foo": ("x", np.random.randn(10))})
        expected = data.assign_coords(c=("x", [0] * 5 + [1] * 5))
        objs = [
            data.isel(x=slice(5)).assign_coords(c=0),
            data.isel(x=slice(5, None)).assign_coords(c=1),
        ]
        for coords in ["different", "all", ["c"]]:
            actual = concat(objs, dim="x", coords=coords)
            assert_identical(expected, actual)
        for coords in ["minimal", []]:
            with raises_regex(merge.MergeError, "conflicting values"):
                concat(objs, dim="x", coords=coords)

    def test_concat_constant_index(self):
        """
        Concatenate two datasets along a shared coordinate 'y'. The function tests the concatenation of datasets with different or identical data variables, and handles conflicts in dimension names. It also demonstrates the use of the `concat` function with various modes and error handling.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        merge.MergeError: If there are conflicting values during concatenation.
        
        Example:
        >>> ds1 = Dataset({"foo": 1.5}, {"y":
        """

        # GH425
        ds1 = Dataset({"foo": 1.5}, {"y": 1})
        ds2 = Dataset({"foo": 2.5}, {"y": 1})
        expected = Dataset({"foo": ("y", [1.5, 2.5]), "y": [1, 1]})
        for mode in ["different", "all", ["foo"]]:
            actual = concat([ds1, ds2], "y", data_vars=mode)
            assert_identical(expected, actual)
        with raises_regex(merge.MergeError, "conflicting values"):
            # previously dim="y", and raised error which makes no sense.
            # "foo" has dimension "y" so minimal should concatenate it?
            concat([ds1, ds2], "new_dim", data_vars="minimal")

    def test_concat_size0(self):
        """
        Concatenates multiple DataArrays or Datasets along a specified dimension, ensuring that the resulting object matches the original data.
        
        Parameters:
        split_data (list): A list containing DataArrays or Datasets with one of them having size 0 along the specified dimension.
        dim1 (str): The dimension along which the concatenation is performed.
        
        Returns:
        DataArray or Dataset: A new concatenated DataArray or Dataset that matches the original data.
        
        Examples:
        >>> data = create
        """

        data = create_test_data()
        split_data = [data.isel(dim1=slice(0, 0)), data]
        actual = concat(split_data, "dim1")
        assert_identical(data, actual)

        actual = concat(split_data[::-1], "dim1")
        assert_identical(data, actual)

    def test_concat_autoalign(self):
        """
        Concatenate two datasets along a new dimension 'y' by aligning coordinates.
        
        This function takes two datasets `ds1` and `ds2`, each containing a single
        data array named 'foo', and concatenates them along a new dimension named
        'y'. The coordinates of the 'foo' data array in both datasets are aligned
        based on their values, resulting in a new dataset with missing values
        (NaN) where there is no corresponding coordinate.
        """

        ds1 = Dataset({"foo": DataArray([1, 2], coords=[("x", [1, 2])])})
        ds2 = Dataset({"foo": DataArray([1, 2], coords=[("x", [1, 3])])})
        actual = concat([ds1, ds2], "y")
        expected = Dataset(
            {
                "foo": DataArray(
                    [[1, 2, np.nan], [1, np.nan, 2]],
                    dims=["y", "x"],
                    coords={"x": [1, 2, 3]},
                )
            }
        )
        assert_identical(expected, actual)

    def test_concat_errors(self):
        """
        Test various error conditions for the `concat` function.
        
        This function tests the `concat` function with different error scenarios,
        including providing no datasets, specifying conflicting options, missing
        coordinates, mismatched global attributes, mismatched variables, invalid
        compatibility settings, incorrect coordinate handling, and concatenation
        along a dimension where coordinates are present in some datasets but not
        others.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: Raised when
        """

        data = create_test_data()
        split_data = [data.isel(dim1=slice(3)), data.isel(dim1=slice(3, None))]

        with raises_regex(ValueError, "must supply at least one"):
            concat([], "dim1")

        with raises_regex(ValueError, "Cannot specify both .*='different'"):
            concat(
                [data, data], dim="concat_dim", data_vars="different", compat="override"
            )

        with raises_regex(ValueError, "must supply at least one"):
            concat([], "dim1")

        with raises_regex(ValueError, "are not coordinates"):
            concat([data, data], "new_dim", coords=["not_found"])

        with raises_regex(ValueError, "global attributes not"):
            data0, data1 = deepcopy(split_data)
            data1.attrs["foo"] = "bar"
            concat([data0, data1], "dim1", compat="identical")
        assert_identical(data, concat([data0, data1], "dim1", compat="equals"))

        with raises_regex(ValueError, "present in some datasets"):
            data0, data1 = deepcopy(split_data)
            data1["foo"] = ("bar", np.random.randn(10))
            concat([data0, data1], "dim1")

        with raises_regex(ValueError, "compat.* invalid"):
            concat(split_data, "dim1", compat="foobar")

        with raises_regex(ValueError, "unexpected value for"):
            concat([data, data], "new_dim", coords="foobar")

        with raises_regex(ValueError, "coordinate in some datasets but not others"):
            concat([Dataset({"x": 0}), Dataset({"x": [1]})], dim="z")

        with raises_regex(ValueError, "coordinate in some datasets but not others"):
            concat([Dataset({"x": 0}), Dataset({}, {"x": 1})], dim="z")

    def test_concat_join_kwarg(self):
        """
        Concatenate multiple datasets along a dimension.
        
        This function concatenates two datasets `ds1` and `ds2` along the dimension
        'x'. The resulting dataset's coordinates and data arrays are determined by
        the specified `join` parameter. The function supports different types of
        joins such as 'outer', 'inner', 'left', 'right', and 'override'.
        
        Parameters:
        - ds1 (Dataset): First dataset containing variable 'a' with coordinates 'x
        """

        ds1 = Dataset({"a": (("x", "y"), [[0]])}, coords={"x": [0], "y": [0]})
        ds2 = Dataset({"a": (("x", "y"), [[0]])}, coords={"x": [1], "y": [0.0001]})

        expected = {}
        expected["outer"] = Dataset(
            {"a": (("x", "y"), [[0, np.nan], [np.nan, 0]])},
            {"x": [0, 1], "y": [0, 0.0001]},
        )
        expected["inner"] = Dataset(
            {"a": (("x", "y"), [[], []])}, {"x": [0, 1], "y": []}
        )
        expected["left"] = Dataset(
            {"a": (("x", "y"), np.array([0, np.nan], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0]},
        )
        expected["right"] = Dataset(
            {"a": (("x", "y"), np.array([np.nan, 0], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0.0001]},
        )
        expected["override"] = Dataset(
            {"a": (("x", "y"), np.array([0, 0], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0]},
        )

        with raises_regex(ValueError, "indexes along dimension 'y'"):
            actual = concat([ds1, ds2], join="exact", dim="x")

        for join in expected:
            actual = concat([ds1, ds2], join=join, dim="x")
            assert_equal(actual, expected[join])

    def test_concat_promote_shape(self):
        """
        Concatenate multiple datasets along a shared dimension.
        
        This function concatenates multiple `xarray.Dataset` objects along a shared
        dimension, handling cases where dimensions are mixed within or between
        variables, and ensuring that coordinates and attributes are appropriately
        aligned and promoted.
        
        Parameters:
        objs (list of xarray.Dataset): The datasets to be concatenated.
        dim (str): The dimension along which to concatenate the datasets.
        
        Returns:
        xarray.Dataset: The concatenated dataset.
        """

        # mixed dims within variables
        objs = [Dataset({}, {"x": 0}), Dataset({"x": [1]})]
        actual = concat(objs, "x")
        expected = Dataset({"x": [0, 1]})
        assert_identical(actual, expected)

        objs = [Dataset({"x": [0]}), Dataset({}, {"x": 1})]
        actual = concat(objs, "x")
        assert_identical(actual, expected)

        # mixed dims between variables
        objs = [Dataset({"x": [2], "y": 3}), Dataset({"x": [4], "y": 5})]
        actual = concat(objs, "x")
        expected = Dataset({"x": [2, 4], "y": ("x", [3, 5])})
        assert_identical(actual, expected)

        # mixed dims in coord variable
        objs = [Dataset({"x": [0]}, {"y": -1}), Dataset({"x": [1]}, {"y": ("x", [-2])})]
        actual = concat(objs, "x")
        expected = Dataset({"x": [0, 1]}, {"y": ("x", [-1, -2])})
        assert_identical(actual, expected)

        # scalars with mixed lengths along concat dim -- values should repeat
        objs = [Dataset({"x": [0]}, {"y": -1}), Dataset({"x": [1, 2]}, {"y": -2})]
        actual = concat(objs, "x")
        expected = Dataset({"x": [0, 1, 2]}, {"y": ("x", [-1, -2, -2])})
        assert_identical(actual, expected)

        # broadcast 1d x 1d -> 2d
        objs = [
            Dataset({"z": ("x", [-1])}, {"x": [0], "y": [0]}),
            Dataset({"z": ("y", [1])}, {"x": [1], "y": [0]}),
        ]
        actual = concat(objs, "x")
        expected = Dataset({"z": (("x", "y"), [[-1], [1]])}, {"x": [0, 1], "y": [0]})
        assert_identical(actual, expected)

    def test_concat_do_not_promote(self):
        """
        Concatenate multiple datasets along a shared dimension.
        
        Parameters:
        -----------
        objs : list of xarray.Dataset
        The datasets to be concatenated.
        dim : str
        The dimension along which to concatenate the datasets.
        
        Returns:
        --------
        xarray.Dataset
        The concatenated dataset.
        
        Raises:
        -------
        ValueError
        If the datasets do not share the same coordinates when `coords='minimal'` is specified.
        
        Examples:
        ---------
        >>> objs = [
        """

        # GH438
        objs = [
            Dataset({"y": ("t", [1])}, {"x": 1, "t": [0]}),
            Dataset({"y": ("t", [2])}, {"x": 1, "t": [0]}),
        ]
        expected = Dataset({"y": ("t", [1, 2])}, {"x": 1, "t": [0, 0]})
        actual = concat(objs, "t")
        assert_identical(expected, actual)

        objs = [
            Dataset({"y": ("t", [1])}, {"x": 1, "t": [0]}),
            Dataset({"y": ("t", [2])}, {"x": 2, "t": [0]}),
        ]
        with pytest.raises(ValueError):
            concat(objs, "t", coords="minimal")

    def test_concat_dim_is_variable(self):
        """
        Concatenates multiple datasets along a variable dimension.
        
        This function takes a list of datasets and a variable coordinate, concatenates
        the datasets along the specified coordinate, and returns the resulting dataset.
        
        Parameters:
        objs (list): A list of `Dataset` objects to be concatenated.
        coord (Variable): The variable coordinate along which the datasets will be concatenated.
        
        Returns:
        Dataset: The concatenated dataset with the specified coordinate.
        
        Example:
        >>> objs = [Dataset({"x
        """

        objs = [Dataset({"x": 0}), Dataset({"x": 1})]
        coord = Variable("y", [3, 4])
        expected = Dataset({"x": ("y", [0, 1]), "y": [3, 4]})
        actual = concat(objs, coord)
        assert_identical(actual, expected)

    def test_concat_multiindex(self):
        """
        Concatenates two subsets of a dataset along the 'x' dimension using `pd.MultiIndex`. The function takes two slices of a MultiIndex dataset and merges them back into a single dataset with the same structure. The resulting dataset's 'x' coordinate is a MultiIndex.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `pd.MultiIndex.from_product`: Creates the initial MultiIndex.
        - `Dataset.isel`: Selects a subset of the
        """

        x = pd.MultiIndex.from_product([[1, 2, 3], ["a", "b"]])
        expected = Dataset({"x": x})
        actual = concat(
            [expected.isel(x=slice(2)), expected.isel(x=slice(2, None))], "x"
        )
        assert expected.equals(actual)
        assert isinstance(actual.x.to_index(), pd.MultiIndex)

    @pytest.mark.parametrize("fill_value", [dtypes.NA, 2, 2.0])
    def test_concat_fill_value(self, fill_value):
        """
        Concatenate multiple Datasets along a new dimension.
        
        Parameters:
        -----------
        datasets : list of xarray.Dataset
        The datasets to concatenate.
        dim : str, optional
        The name of the new dimension to create. Default is 't'.
        fill_value : float or None, optional
        The fill value to use for missing values. If `dtypes.NA` is provided,
        the default fill value for the data type will be used. Default is None.
        """

        datasets = [
            Dataset({"a": ("x", [2, 3]), "x": [1, 2]}),
            Dataset({"a": ("x", [1, 2]), "x": [0, 1]}),
        ]
        if fill_value == dtypes.NA:
            # if we supply the default, we expect the missing value for a
            # float array
            fill_value = np.nan
        expected = Dataset(
            {"a": (("t", "x"), [[fill_value, 2, 3], [1, 2, fill_value]])},
            {"x": [0, 1, 2]},
        )
        actual = concat(datasets, dim="t", fill_value=fill_value)
        assert_identical(actual, expected)


class TestConcatDataArray:
    def test_concat(self):
        """
        Concatenate multiple Dataset or DataArray objects along a new dimension.
        
        Parameters:
        -----------
        - objects : list of Dataset or DataArray objects
        The objects to be concatenated.
        - dim : str, optional
        The name of the new dimension along which to concatenate.
        - compat : {'broadcast', 'equals', 'identical'}, optional
        Controls how strict the comparison between objects should be.
        - data_vars : {'mean', 'broadcast', 'override', '
        """

        ds = Dataset(
            {
                "foo": (["x", "y"], np.random.random((2, 3))),
                "bar": (["x", "y"], np.random.random((2, 3))),
            },
            {"x": [0, 1]},
        )
        foo = ds["foo"]
        bar = ds["bar"]

        # from dataset array:
        expected = DataArray(
            np.array([foo.values, bar.values]),
            dims=["w", "x", "y"],
            coords={"x": [0, 1]},
        )
        actual = concat([foo, bar], "w")
        assert_equal(expected, actual)
        # from iteration:
        grouped = [g for _, g in foo.groupby("x")]
        stacked = concat(grouped, ds["x"])
        assert_identical(foo, stacked)
        # with an index as the 'dim' argument
        stacked = concat(grouped, ds.indexes["x"])
        assert_identical(foo, stacked)

        actual = concat([foo[0], foo[1]], pd.Index([0, 1])).reset_coords(drop=True)
        expected = foo[:2].rename({"x": "concat_dim"})
        assert_identical(expected, actual)

        actual = concat([foo[0], foo[1]], [0, 1]).reset_coords(drop=True)
        expected = foo[:2].rename({"x": "concat_dim"})
        assert_identical(expected, actual)

        with raises_regex(ValueError, "not identical"):
            concat([foo, bar], dim="w", compat="identical")

        with raises_regex(ValueError, "not a valid argument"):
            concat([foo, bar], dim="w", data_vars="minimal")

    def test_concat_encoding(self):
        """
        Concatenates datasets or data arrays along an unlimited dimension while preserving the encoding of the original dataset or data array.
        
        This function tests the behavior of `xarray.concat` when applied to datasets or data arrays with custom encodings. Specifically, it ensures that the encoding of the concatenated result matches the encoding of the original dataset or data array.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `xarray.Dataset`: The input dataset containing the data arrays
        """

        # Regression test for GH1297
        ds = Dataset(
            {
                "foo": (["x", "y"], np.random.random((2, 3))),
                "bar": (["x", "y"], np.random.random((2, 3))),
            },
            {"x": [0, 1]},
        )
        foo = ds["foo"]
        foo.encoding = {"complevel": 5}
        ds.encoding = {"unlimited_dims": "x"}
        assert concat([foo, foo], dim="x").encoding == foo.encoding
        assert concat([ds, ds], dim="x").encoding == ds.encoding

    @requires_dask
    def test_concat_lazy(self):
        """
        Concatenate multiple Dask-backed DataArrays along a new dimension.
        
        Parameters:
        -----------
        arrays : list of DataArray
        A list of DataArrays with Dask-backed arrays.
        
        Returns:
        --------
        combined : DataArray
        The concatenated DataArray with an additional dimension.
        
        Notes:
        ------
        - The input DataArrays must have compatible shapes except along the
        concatenation dimension.
        - The resulting DataArray will have the new dimension named 'z'
        """

        import dask.array as da

        arrays = [
            DataArray(
                da.from_array(InaccessibleArray(np.zeros((3, 3))), 3), dims=["x", "y"]
            )
            for _ in range(2)
        ]
        # should not raise
        combined = concat(arrays, dim="z")
        assert combined.shape == (2, 3, 3)
        assert combined.dims == ("z", "x", "y")

    @pytest.mark.parametrize("fill_value", [dtypes.NA, 2, 2.0])
    def test_concat_fill_value(self, fill_value):
        """
        Concatenate multiple :class:`DataArray` objects along a new dimension.
        
        Parameters
        ----------
        fill_value : float or None
        The fill value to use for missing values. If set to `dtypes.NA`, the
        default fill value for the data type of the arrays will be used.
        
        Returns
        -------
        :class:`DataArray`
        The concatenated :class:`DataArray` with an additional dimension.
        
        Examples
        --------
        >>> foo = Data
        """

        foo = DataArray([1, 2], coords=[("x", [1, 2])])
        bar = DataArray([1, 2], coords=[("x", [1, 3])])
        if fill_value == dtypes.NA:
            # if we supply the default, we expect the missing value for a
            # float array
            fill_value = np.nan
        expected = DataArray(
            [[1, 2, fill_value], [1, fill_value, 2]],
            dims=["y", "x"],
            coords={"x": [1, 2, 3]},
        )
        actual = concat((foo, bar), dim="y", fill_value=fill_value)
        assert_identical(actual, expected)

    def test_concat_join_kwarg(self):
        """
        Concatenate multiple datasets along a dimension.
        
        This function concatenates two datasets along the 'x' dimension using different
        join strategies ('outer', 'inner', 'left', 'right', 'override') and checks if the
        resulting dataset matches the expected output.
        
        Parameters:
        - ds1 (Dataset): First dataset containing an array 'a' with coordinates 'x' and 'y'.
        - ds2 (Dataset): Second dataset containing an array 'a' with coordinates '
        """

        ds1 = Dataset(
            {"a": (("x", "y"), [[0]])}, coords={"x": [0], "y": [0]}
        ).to_array()
        ds2 = Dataset(
            {"a": (("x", "y"), [[0]])}, coords={"x": [1], "y": [0.0001]}
        ).to_array()

        expected = {}
        expected["outer"] = Dataset(
            {"a": (("x", "y"), [[0, np.nan], [np.nan, 0]])},
            {"x": [0, 1], "y": [0, 0.0001]},
        )
        expected["inner"] = Dataset(
            {"a": (("x", "y"), [[], []])}, {"x": [0, 1], "y": []}
        )
        expected["left"] = Dataset(
            {"a": (("x", "y"), np.array([0, np.nan], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0]},
        )
        expected["right"] = Dataset(
            {"a": (("x", "y"), np.array([np.nan, 0], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0.0001]},
        )
        expected["override"] = Dataset(
            {"a": (("x", "y"), np.array([0, 0], ndmin=2).T)},
            coords={"x": [0, 1], "y": [0]},
        )

        with raises_regex(ValueError, "indexes along dimension 'y'"):
            actual = concat([ds1, ds2], join="exact", dim="x")

        for join in expected:
            actual = concat([ds1, ds2], join=join, dim="x")
            assert_equal(actual, expected[join].to_array())
