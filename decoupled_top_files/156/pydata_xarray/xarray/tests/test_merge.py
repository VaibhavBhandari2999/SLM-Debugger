import numpy as np
import pytest

import xarray as xr
from xarray.core import dtypes, merge

from . import raises_regex
from .test_dataset import create_test_data


class TestMergeInternals:
    def test_broadcast_dimension_size(self):
        """
        Test the `broadcast_dimension_size` function.
        
        This function checks the size of broadcasted dimensions for given variables.
        It returns a dictionary mapping dimension names to their sizes.
        
        Args:
        variables (List[xr.Variable]): A list of xarray Variables.
        
        Returns:
        Dict[str, int]: A dictionary mapping dimension names to their sizes.
        
        Raises:
        ValueError: If the dimensions cannot be broadcasted correctly.
        
        Examples:
        >>> merge.broadcast_dimension_size([xr.Variable("x
        """

        actual = merge.broadcast_dimension_size(
            [xr.Variable("x", [1]), xr.Variable("y", [2, 1])]
        )
        assert actual == {"x": 1, "y": 2}

        actual = merge.broadcast_dimension_size(
            [xr.Variable(("x", "y"), [[1, 2]]), xr.Variable("y", [2, 1])]
        )
        assert actual == {"x": 1, "y": 2}

        with pytest.raises(ValueError):
            merge.broadcast_dimension_size(
                [xr.Variable(("x", "y"), [[1, 2]]), xr.Variable("y", [2])]
            )


class TestMergeFunction:
    def test_merge_arrays(self):
        """
        Merge two xarray DataArrays into a single dataset.
        
        This function takes a dictionary containing two xarray DataArrays (`var1` and `var2`) and merges them into a single xarray Dataset. The resulting dataset contains both variables.
        
        Parameters:
        -----------
        None (The function uses pre-defined test data)
        
        Returns:
        --------
        None (The function asserts the equality of the merged result with the expected output)
        
        Important Functions:
        --------------------
        - `xr.merge
        """

        data = create_test_data()
        actual = xr.merge([data.var1, data.var2])
        expected = data[["var1", "var2"]]
        assert actual.identical(expected)

    def test_merge_datasets(self):
        """
        Merge multiple datasets along shared dimensions.
        
        This function merges two or more xarray datasets along their shared
        dimensions. It supports merging datasets with overlapping variables,
        ensuring that the resulting dataset contains all variables from the
        input datasets.
        
        Parameters:
        None (The function uses predefined test data).
        
        Returns:
        None (The function asserts the correctness of the merged datasets).
        
        Keywords and Functions:
        - `xr.merge`: Merges multiple xarray datasets.
        - `create
        """

        data = create_test_data()

        actual = xr.merge([data[["var1"]], data[["var2"]]])
        expected = data[["var1", "var2"]]
        assert actual.identical(expected)

        actual = xr.merge([data, data])
        assert actual.identical(data)

    def test_merge_dataarray_unnamed(self):
        """
        Merge a list of DataArrays into a single dataset. If the DataArrays do not have named dimensions, a `ValueError` is raised.
        
        Parameters:
        -----------
        data : xr.DataArray
        The input DataArray to be merged.
        
        Raises:
        -------
        ValueError
        If the DataArray does not have named dimensions.
        
        Examples:
        ---------
        >>> data = xr.DataArray([1, 2], dims="x")
        >>> with raises_regex(ValueError,
        """

        data = xr.DataArray([1, 2], dims="x")
        with raises_regex(ValueError, "without providing an explicit name"):
            xr.merge([data])

    def test_merge_dicts_simple(self):
        """
        Merge multiple dictionaries into a single xarray.Dataset.
        
        This function takes a list of dictionaries containing key-value pairs and
        merges them into a single xarray.Dataset. The keys from each dictionary are
        combined into the resulting dataset, with values from later dictionaries
        overwriting those from earlier ones if there are duplicate keys.
        
        Args:
        dicts (list): A list of dictionaries to be merged.
        
        Returns:
        xarray.Dataset: A new xarray.Dataset containing the merged key
        """

        actual = xr.merge([{"foo": 0}, {"bar": "one"}, {"baz": 3.5}])
        expected = xr.Dataset({"foo": 0, "bar": "one", "baz": 3.5})
        assert actual.identical(expected)

    def test_merge_dicts_dims(self):
        """
        Merge dictionaries of xarray datasets or data arrays into a single dataset.
        
        Args:
        dicts (list): A list of dictionaries, where each dictionary contains
        xarray datasets or data arrays with compatible dimensions.
        
        Returns:
        xr.Dataset: The merged dataset containing all the variables from the input dictionaries.
        
        Example:
        >>> actual = xr.merge([{"y": ("x", [13])}, {"x": [12]}])
        >>> expected = xr.Dataset({"x":
        """

        actual = xr.merge([{"y": ("x", [13])}, {"x": [12]}])
        expected = xr.Dataset({"x": [12], "y": ("x", [13])})
        assert actual.identical(expected)

    def test_merge_error(self):
        """
        Test merging two datasets that cannot be merged due to differing data values.
        
        This function raises an `xr.MergeError` when attempting to merge a dataset
        `ds` with its modified version `ds + 1`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        xr.MergeError: When attempting to merge the original dataset with its modified version.
        
        Important Functions:
        - `xr.Dataset`: Creates a dataset object.
        - `xr.merge`: Merg
        """

        ds = xr.Dataset({"x": 0})
        with pytest.raises(xr.MergeError):
            xr.merge([ds, ds + 1])

    def test_merge_alignment_error(self):
        """
        Merge two datasets with exact join, raising an error if the indexes do not match. This function takes two xarray Datasets, `ds` and `other`, and attempts to merge them using an 'exact' join. If the indexes on the 'x' coordinate do not match between the two datasets, a ValueError is raised with a specific regex pattern.
        
        Parameters:
        ds (xr.Dataset): The first dataset with coordinates.
        other (xr.Dataset): The second dataset with coordinates.
        """

        ds = xr.Dataset(coords={"x": [1, 2]})
        other = xr.Dataset(coords={"x": [2, 3]})
        with raises_regex(ValueError, "indexes .* not equal"):
            xr.merge([ds, other], join="exact")

    def test_merge_wrong_input_error(self):
        """
        Test merging datasets and dataarrays with incorrect input types.
        
        This function checks that `xr.merge` raises a TypeError with appropriate
        error messages when given non-iterable inputs. It tests three scenarios:
        - Merging a single non-iterable object (raises TypeError).
        - Merging a dictionary containing a dataset (raises TypeError).
        - Merging a list containing a dataset and a non-iterable object (raises TypeError).
        
        Parameters:
        None
        
        Returns:
        """

        with raises_regex(TypeError, "objects must be an iterable"):
            xr.merge([1])
        ds = xr.Dataset(coords={"x": [1, 2]})
        with raises_regex(TypeError, "objects must be an iterable"):
            xr.merge({"a": ds})
        with raises_regex(TypeError, "objects must be an iterable"):
            xr.merge([ds, 1])

    def test_merge_no_conflicts_single_var(self):
        """
        Merge two or more xarray datasets without conflicts, ensuring that the resulting dataset has no conflicting dimensions or variables. The function supports different merge strategies such as 'no_conflicts', 'left', 'right', and 'inner'.
        
        Parameters:
        - ds1, ds2: xarray.Datasets to be merged.
        - compat: String specifying the compatibility mode ('no_conflicts', 'left', 'right', 'inner').
        - join: String specifying the join type ('left',
        """

        ds1 = xr.Dataset({"a": ("x", [1, 2]), "x": [0, 1]})
        ds2 = xr.Dataset({"a": ("x", [2, 3]), "x": [1, 2]})
        expected = xr.Dataset({"a": ("x", [1, 2, 3]), "x": [0, 1, 2]})
        assert expected.identical(xr.merge([ds1, ds2], compat="no_conflicts"))
        assert expected.identical(xr.merge([ds2, ds1], compat="no_conflicts"))
        assert ds1.identical(xr.merge([ds1, ds2], compat="no_conflicts", join="left"))
        assert ds2.identical(xr.merge([ds1, ds2], compat="no_conflicts", join="right"))
        expected = xr.Dataset({"a": ("x", [2]), "x": [1]})
        assert expected.identical(
            xr.merge([ds1, ds2], compat="no_conflicts", join="inner")
        )

        with pytest.raises(xr.MergeError):
            ds3 = xr.Dataset({"a": ("x", [99, 3]), "x": [1, 2]})
            xr.merge([ds1, ds3], compat="no_conflicts")

        with pytest.raises(xr.MergeError):
            ds3 = xr.Dataset({"a": ("y", [2, 3]), "y": [1, 2]})
            xr.merge([ds1, ds3], compat="no_conflicts")

    def test_merge_no_conflicts_multi_var(self):
        """
        Merge multiple xarray datasets or DataArrays with 'no_conflicts' compatibility check.
        
        This function merges two or more xarray datasets or DataArrays using the 'no_conflicts'
        compatibility check. It ensures that variables with the same name are not conflicting,
        meaning they should have the same shape and values where they overlap.
        
        Parameters:
        - data (xarray.Dataset): The first dataset or DataArray to merge.
        - data1 (xarray.Dataset): The second dataset or
        """

        data = create_test_data()
        data1 = data.copy(deep=True)
        data2 = data.copy(deep=True)

        expected = data[["var1", "var2"]]
        actual = xr.merge([data1.var1, data2.var2], compat="no_conflicts")
        assert expected.identical(actual)

        data1["var1"][:, :5] = np.nan
        data2["var1"][:, 5:] = np.nan
        data1["var2"][:4, :] = np.nan
        data2["var2"][4:, :] = np.nan
        del data2["var3"]

        actual = xr.merge([data1, data2], compat="no_conflicts")
        assert data.equals(actual)

    def test_merge_no_conflicts_preserve_attrs(self):
        """
        Merge two identical `xr.Dataset` objects without conflicts and preserve their attributes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Summary:
        This function takes two identical `xr.Dataset` objects and merges them using `xr.merge`. The merged dataset is expected to be identical to the original dataset, and the function asserts that this is the case by comparing the original and merged datasets for equality. The attributes of the original datasets are preserved during the merge process.
        
        Important Functions:
        -
        """

        data = xr.Dataset({"x": ([], 0, {"foo": "bar"})})
        actual = xr.merge([data, data])
        assert data.identical(actual)

    def test_merge_no_conflicts_broadcast(self):
        """
        Merge multiple xarray datasets into a single dataset, handling cases where there are no conflicts between the datasets. The function uses `xr.merge` to combine the datasets. If any of the datasets contain NaN values, they are treated appropriately to avoid conflicts.
        
        Parameters:
        None (The function is testing the `xr.merge` function with predefined datasets.)
        
        Returns:
        None (The function asserts that the merged dataset matches an expected dataset.)
        
        Important Functions:
        - `xr.Dataset`: Used to
        """

        datasets = [xr.Dataset({"x": ("y", [0])}), xr.Dataset({"x": np.nan})]
        actual = xr.merge(datasets)
        expected = xr.Dataset({"x": ("y", [0])})
        assert expected.identical(actual)

        datasets = [xr.Dataset({"x": ("y", [np.nan])}), xr.Dataset({"x": 0})]
        actual = xr.merge(datasets)
        assert expected.identical(actual)


class TestMergeMethod:
    def test_merge(self):
        """
        Tests the merge functionality of xarray datasets.
        
        This function tests the merge operation on various combinations of datasets
        and ensures that the resulting merged dataset matches the expected output.
        The merge operation is performed using the `merge` method of xarray datasets.
        The function creates test data using the `create_test_data` function and
        manipulates it by selecting specific variables, renaming variables, and
        resetting coordinates. It then performs the merge operation and asserts
        that the result is
        """

        data = create_test_data()
        ds1 = data[["var1"]]
        ds2 = data[["var3"]]
        expected = data[["var1", "var3"]]
        actual = ds1.merge(ds2)
        assert expected.identical(actual)

        actual = ds2.merge(ds1)
        assert expected.identical(actual)

        actual = data.merge(data)
        assert data.identical(actual)
        actual = data.reset_coords(drop=True).merge(data)
        assert data.identical(actual)
        actual = data.merge(data.reset_coords(drop=True))
        assert data.identical(actual)

        with pytest.raises(ValueError):
            ds1.merge(ds2.rename({"var3": "var1"}))
        with raises_regex(ValueError, "should be coordinates or not"):
            data.reset_coords().merge(data)
        with raises_regex(ValueError, "should be coordinates or not"):
            data.merge(data.reset_coords())

    def test_merge_broadcast_equals(self):
        """
        Tests the merge and update functionalities of xarray datasets.
        
        This function tests the `merge` method of xarray datasets by comparing
        the results with the expected output using the `identical` method. It
        verifies that merging an empty dataset (`ds1`) with a dataset containing
        a broadcasted variable (`ds2`) yields the same result regardless of the
        order of merging. Additionally, it checks if updating `ds1` with `ds2`
        using the
        """

        ds1 = xr.Dataset({"x": 0})
        ds2 = xr.Dataset({"x": ("y", [0, 0])})
        actual = ds1.merge(ds2)
        assert ds2.identical(actual)

        actual = ds2.merge(ds1)
        assert ds2.identical(actual)

        actual = ds1.copy()
        actual.update(ds2)
        assert ds2.identical(actual)

        ds1 = xr.Dataset({"x": np.nan})
        ds2 = xr.Dataset({"x": ("y", [np.nan, np.nan])})
        actual = ds1.merge(ds2)
        assert ds2.identical(actual)

    def test_merge_compat(self):
        """
        Tests merging datasets with different compatibility settings.
        
        This function tests the `merge` method of xarray's Dataset class by
        attempting to merge two datasets under various compatibility settings.
        The important keywords and functions used include:
        
        - `xr.Dataset`: The input datasets.
        - `xr.MergeError`: Raised when merging fails due to incompatible data.
        - `raises_regex`: Used to assert that a specific error message is raised.
        - `identical`: Checks if two datasets are identical
        """

        ds1 = xr.Dataset({"x": 0})
        ds2 = xr.Dataset({"x": 1})
        for compat in ["broadcast_equals", "equals", "identical", "no_conflicts"]:
            with pytest.raises(xr.MergeError):
                ds1.merge(ds2, compat=compat)

        ds2 = xr.Dataset({"x": [0, 0]})
        for compat in ["equals", "identical"]:
            with raises_regex(ValueError, "should be coordinates or not"):
                ds1.merge(ds2, compat=compat)

        ds2 = xr.Dataset({"x": ((), 0, {"foo": "bar"})})
        with pytest.raises(xr.MergeError):
            ds1.merge(ds2, compat="identical")

        with raises_regex(ValueError, "compat=.* invalid"):
            ds1.merge(ds2, compat="foobar")

        assert ds1.identical(ds1.merge(ds2, compat="override"))

    def test_merge_auto_align(self):
        """
        Merge two xarray datasets along their shared dimensions, with automatic alignment. The function supports different merge strategies such as 'auto', 'left', 'right', and 'inner'.
        
        Parameters:
        - ds1 (xr.Dataset): First dataset to be merged.
        - ds2 (xr.Dataset): Second dataset to be merged.
        
        Returns:
        - xr.Dataset: Merged dataset with aligned coordinates and variables.
        
        Examples:
        - When using 'auto' or 'inner' strategy,
        """

        ds1 = xr.Dataset({"a": ("x", [1, 2]), "x": [0, 1]})
        ds2 = xr.Dataset({"b": ("x", [3, 4]), "x": [1, 2]})
        expected = xr.Dataset(
            {"a": ("x", [1, 2, np.nan]), "b": ("x", [np.nan, 3, 4])}, {"x": [0, 1, 2]}
        )
        assert expected.identical(ds1.merge(ds2))
        assert expected.identical(ds2.merge(ds1))

        expected = expected.isel(x=slice(2))
        assert expected.identical(ds1.merge(ds2, join="left"))
        assert expected.identical(ds2.merge(ds1, join="right"))

        expected = expected.isel(x=slice(1, 2))
        assert expected.identical(ds1.merge(ds2, join="inner"))
        assert expected.identical(ds2.merge(ds1, join="inner"))

    @pytest.mark.parametrize("fill_value", [dtypes.NA, 2, 2.0])
    def test_merge_fill_value(self, fill_value):
        """
        Merge two or more datasets along their dimensions, filling missing values with a specified fill value.
        
        Parameters:
        -----------
        fill_value : scalar or np.nan
        The value to use for filling missing coordinates in the merged dataset.
        
        Returns:
        --------
        merged_dataset : xarray.Dataset
        The resulting dataset after merging the input datasets.
        
        Examples:
        ---------
        >>> ds1 = xr.Dataset({"a": ("x", [1, 2]), "x": [0
        """

        ds1 = xr.Dataset({"a": ("x", [1, 2]), "x": [0, 1]})
        ds2 = xr.Dataset({"b": ("x", [3, 4]), "x": [1, 2]})
        if fill_value == dtypes.NA:
            # if we supply the default, we expect the missing value for a
            # float array
            fill_value = np.nan
        expected = xr.Dataset(
            {"a": ("x", [1, 2, fill_value]), "b": ("x", [fill_value, 3, 4])},
            {"x": [0, 1, 2]},
        )
        assert expected.identical(ds1.merge(ds2, fill_value=fill_value))
        assert expected.identical(ds2.merge(ds1, fill_value=fill_value))
        assert expected.identical(xr.merge([ds1, ds2], fill_value=fill_value))

    def test_merge_no_conflicts(self):
        """
        Merge two xarray datasets without conflicts.
        
        This function merges two xarray datasets (`ds1` and `ds2`) using the
        'no_conflicts' compatibility check. The resulting dataset will have
        combined data from both inputs where there are no conflicting dimensions
        or variables.
        
        Parameters:
        - ds1 (xr.Dataset): First input dataset.
        - ds2 (xr.Dataset): Second input dataset.
        
        Returns:
        - xr.Dataset: Merged dataset with no
        """

        ds1 = xr.Dataset({"a": ("x", [1, 2]), "x": [0, 1]})
        ds2 = xr.Dataset({"a": ("x", [2, 3]), "x": [1, 2]})
        expected = xr.Dataset({"a": ("x", [1, 2, 3]), "x": [0, 1, 2]})

        assert expected.identical(ds1.merge(ds2, compat="no_conflicts"))
        assert expected.identical(ds2.merge(ds1, compat="no_conflicts"))

        assert ds1.identical(ds1.merge(ds2, compat="no_conflicts", join="left"))

        assert ds2.identical(ds1.merge(ds2, compat="no_conflicts", join="right"))

        expected2 = xr.Dataset({"a": ("x", [2]), "x": [1]})
        assert expected2.identical(ds1.merge(ds2, compat="no_conflicts", join="inner"))

        with pytest.raises(xr.MergeError):
            ds3 = xr.Dataset({"a": ("x", [99, 3]), "x": [1, 2]})
            ds1.merge(ds3, compat="no_conflicts")

        with pytest.raises(xr.MergeError):
            ds3 = xr.Dataset({"a": ("y", [2, 3]), "y": [1, 2]})
            ds1.merge(ds3, compat="no_conflicts")
