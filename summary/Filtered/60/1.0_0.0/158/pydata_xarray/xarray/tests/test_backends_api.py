import pytest

from xarray.backends.api import _get_default_engine

from . import requires_netCDF4, requires_scipy


@requires_netCDF4
@requires_scipy
def test__get_default_engine():
    """
    Function to determine the default engine for opening a file.
    
    Parameters:
    filepath (str): The path to the file to be opened.
    allow_remote (bool, optional): Whether to allow remote file access. Defaults to False.
    
    Returns:
    str: The name of the default engine to use for opening the file.
    
    Raises:
    ValueError: If the file type is not supported and no default engine can be determined.
    
    Examples:
    >>> _get_default_engine("http://example.org/test.nc",
    """

    engine_remote = _get_default_engine("http://example.org/test.nc", allow_remote=True)
    assert engine_remote == "netcdf4"

    engine_gz = _get_default_engine("/example.gz")
    assert engine_gz == "scipy"

    with pytest.raises(ValueError):
        _get_default_engine("/example.grib")

    engine_default = _get_default_engine("/example")
    assert engine_default == "netcdf4"
