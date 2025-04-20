import pickle

import pytest

import xarray as xr

from . import raises_regex


@xr.register_dataset_accessor("example_accessor")
@xr.register_dataarray_accessor("example_accessor")
class ExampleAccessor:
    """For the pickling tests below."""

    def __init__(self, xarray_obj):
        self.obj = xarray_obj


class TestAccessor:
    def test_register(self):
        """
        Tests the functionality of the `DemoAccessor` class, which is registered as an accessor for both `xr.Dataset` and `xr.DataArray` objects. The accessor provides a `foo` property that returns 'bar'. The test checks that the accessor is correctly registered, can be accessed via the `demo` attribute, and is cached. It also verifies that the descriptor properties are correctly set and that the accessor can be removed and re-registered with a warning.
        
        Key Parameters:
        - `self`:
        """

        @xr.register_dataset_accessor("demo")
        @xr.register_dataarray_accessor("demo")
        class DemoAccessor:
            """Demo accessor."""

            def __init__(self, xarray_obj):
                self._obj = xarray_obj

            @property
            def foo(self):
                return "bar"

        ds = xr.Dataset()
        assert ds.demo.foo == "bar"

        da = xr.DataArray(0)
        assert da.demo.foo == "bar"

        # accessor is cached
        assert ds.demo is ds.demo

        # check descriptor
        assert ds.demo.__doc__ == "Demo accessor."
        assert xr.Dataset.demo.__doc__ == "Demo accessor."
        assert isinstance(ds.demo, DemoAccessor)
        assert xr.Dataset.demo is DemoAccessor

        # ensure we can remove it
        del xr.Dataset.demo
        assert not hasattr(xr.Dataset, "demo")

        with pytest.warns(Warning, match="overriding a preexisting attribute"):

            @xr.register_dataarray_accessor("demo")
            class Foo:
                pass

        # it didn't get registered again
        assert not hasattr(xr.Dataset, "demo")

    def test_pickle_dataset(self):
        """
        Test pickling of an xarray Dataset.
        
        This function pickles and unpickles an xarray Dataset to ensure that the dataset and its associated accessor are correctly restored.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create an xarray Dataset.
        2. Serialize the Dataset using pickle.
        3. Deserialize the Dataset using pickle.
        4. Assert that the original and restored Datasets are identical.
        5. Verify that the accessor state is preserved during serialization and deserialization.
        6
        """

        ds = xr.Dataset()
        ds_restored = pickle.loads(pickle.dumps(ds))
        assert ds.identical(ds_restored)

        # state save on the accessor is restored
        assert ds.example_accessor is ds.example_accessor
        ds.example_accessor.value = "foo"
        ds_restored = pickle.loads(pickle.dumps(ds))
        assert ds.identical(ds_restored)
        assert ds_restored.example_accessor.value == "foo"

    def test_pickle_dataarray(self):
        """
        Test pickling of DataArray objects.
        
        This function checks if a DataArray object remains identical to its unpickled version.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Create an empty Dataset.
        2. Assert that the example_accessor attribute of the original Dataset is the same as the original.
        3. Serialize the Dataset using pickle and then deserialize it.
        4. Assert that the original Dataset is identical to the deserialized version.
        """

        array = xr.Dataset()
        assert array.example_accessor is array.example_accessor
        array_restored = pickle.loads(pickle.dumps(array))
        assert array.identical(array_restored)

    def test_broken_accessor(self):
        # regression test for GH933

        @xr.register_dataset_accessor("stupid_accessor")
        class BrokenAccessor:
            def __init__(self, xarray_obj):
                raise AttributeError("broken")

        with raises_regex(RuntimeError, "error initializing"):
            xr.Dataset().stupid_accessor
