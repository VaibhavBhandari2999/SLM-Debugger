from _pytest.compat import importlib_metadata


def test_pytest_entry_points_are_identical():
    """
    Tests whether the entry points 'pytest' and 'py.test' in the 'pytest' distribution are identical.
    
    This function imports the 'pytest' distribution and retrieves its entry points. It then checks if the entry points for 'pytest' and 'py.test' are the same.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    None
    
    Notes:
    - The function uses the `importlib_metadata` module to work with distribution entry points.
    - The entry points are expected to
    """

    dist = importlib_metadata.distribution("pytest")
    entry_map = {ep.name: ep for ep in dist.entry_points}
    assert entry_map["pytest"].value == entry_map["py.test"].value
