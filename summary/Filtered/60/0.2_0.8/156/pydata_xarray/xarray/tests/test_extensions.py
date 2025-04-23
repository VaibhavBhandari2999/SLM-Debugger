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
        Tests the registration of custom accessors for Xarray Dataset and DataArray objects.
        
        This test function ensures that custom accessors can be registered for Xarray Dataset and DataArray objects, and that these accessors behave as expected. The test checks the following:
        - The accessor can be accessed and returns the expected value.
        - The accessor is cached, meaning that multiple accesses to the same object return the same instance.
        - The accessor's docstring is correctly set.
        - The accessor can be removed and the
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
        array = xr.Dataset()
        assert array.example_accessor is array.example_accessor
        array_restored = pickle.loads(pickle.dumps(array))
        assert array.identical(array_restored)

    def test_broken_accessor(self):
        """
        Test for a broken accessor in an Xarray Dataset.
        
        This test is designed to verify that the Xarray library correctly handles
        errors when initializing a custom dataset accessor. Specifically, it checks
        that a `RuntimeError` is raised with an appropriate error message when the
        accessor's `__init__` method raises an `AttributeError`.
        
        Key Parameters:
        None
        
        Key Returns:
        None
        
        Raises:
        RuntimeError: If the accessor's `__init__` method does not raise an
        """

        # regression test for GH933

        @xr.register_dataset_accessor("stupid_accessor")
        class BrokenAccessor:
            def __init__(self, xarray_obj):
                raise AttributeError("broken")

        with raises_regex(RuntimeError, "error initializing"):
            xr.Dataset().stupid_accessor
