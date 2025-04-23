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
        Tests the functionality of the `DemoAccessor` class, which is registered as an accessor for both `xarray.Dataset` and `xarray.DataArray` objects. The accessor provides a `foo` property that returns 'bar'. The test ensures that the accessor is correctly registered, cached, and can be removed. It also checks that attempting to register an accessor with an existing name triggers a warning and does not overwrite the existing attribute.
        
        Key Parameters:
        - None
        
        Key Return Values:
        - None
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
        Test for broken accessor initialization.
        
        This test ensures that a runtime error is raised when an accessor class
        fails to initialize properly. The accessor class `BrokenAccessor` is
        registered with `xr.register_dataset_accessor` and raises an `AttributeError`
        during initialization. The test checks that a `RuntimeError` is raised with
        the appropriate error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RuntimeError: If the accessor initialization does not raise the expected
        error message.
        """

        # regression test for GH933

        @xr.register_dataset_accessor("stupid_accessor")
        class BrokenAccessor:
            def __init__(self, xarray_obj):
                raise AttributeError("broken")

        with raises_regex(RuntimeError, "error initializing"):
            xr.Dataset().stupid_accessor
