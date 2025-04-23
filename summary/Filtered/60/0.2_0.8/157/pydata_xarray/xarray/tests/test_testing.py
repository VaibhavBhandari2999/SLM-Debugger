import pytest

import xarray as xr


def test_allclose_regression():
    """
    Assert that two DataArrays are all close within a tolerance.
    
    Parameters:
    x (xr.DataArray): The first DataArray to compare.
    y (xr.DataArray): The second DataArray to compare.
    atol (float): The absolute tolerance parameter.
    
    This function checks if two DataArrays are all close to each other within the specified absolute tolerance.
    """

    x = xr.DataArray(1.01)
    y = xr.DataArray(1.02)
    xr.testing.assert_allclose(x, y, atol=0.01)


@pytest.mark.parametrize(
    "obj1,obj2",
    (
        pytest.param(
            xr.Variable("x", [1e-17, 2]), xr.Variable("x", [0, 3]), id="Variable",
        ),
        pytest.param(
            xr.DataArray([1e-17, 2], dims="x"),
            xr.DataArray([0, 3], dims="x"),
            id="DataArray",
        ),
        pytest.param(
            xr.Dataset({"a": ("x", [1e-17, 2]), "b": ("y", [-2e-18, 2])}),
            xr.Dataset({"a": ("x", [0, 2]), "b": ("y", [0, 1])}),
            id="Dataset",
        ),
    ),
)
def test_assert_allclose(obj1, obj2):
    with pytest.raises(AssertionError):
        xr.testing.assert_allclose(obj1, obj2)
