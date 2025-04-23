import pickle

import pytest

import xarray as xr

from . import assert_identical, raises_regex


@xr.register_dataset_accessor("example_accessor")
@xr.register_dataarray_accessor("example_accessor")
class ExampleAccessor:
    """For the pickling tests below."""

    def __init__(self, xarray_obj):
        self.obj = xarray_obj


class TestAccessor:
    def test_register(self):
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
        Test pickling of xarray Dataset.
        
        This function pickles and unpickles an xarray Dataset to ensure that the
        original and restored datasets are identical. It also checks that the state
        of the example accessor is preserved during the pickling and unpickling process.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The original dataset is identical to the restored dataset.
        - The state of the example accessor is preserved in the restored dataset.
        """

        ds = xr.Dataset()
        ds_restored = pickle.loads(pickle.dumps(ds))
        assert_identical(ds, ds_restored)

        # state save on the accessor is restored
        assert ds.example_accessor is ds.example_accessor
        ds.example_accessor.value = "foo"
        ds_restored = pickle.loads(pickle.dumps(ds))
        assert_identical(ds, ds_restored)
        assert ds_restored.example_accessor.value == "foo"

    def test_pickle_dataarray(self):
        """
        Test pickling of DataArray objects.
        
        This function checks if a DataArray object remains identical to itself after being pickled and unpickled.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The original DataArray object and the restored DataArray object are identical.
        - The accessor attribute of the original DataArray object is the same as the accessor attribute of the restored DataArray object.
        """

        array = xr.Dataset()
        assert array.example_accessor is array.example_accessor
        array_restored = pickle.loads(pickle.dumps(array))
        assert_identical(array, array_restored)

    def test_broken_accessor(self):
        # regression test for GH933

        @xr.register_dataset_accessor("stupid_accessor")
        class BrokenAccessor:
            def __init__(self, xarray_obj):
                raise AttributeError("broken")

        with raises_regex(RuntimeError, "error initializing"):
            xr.Dataset().stupid_accessor
