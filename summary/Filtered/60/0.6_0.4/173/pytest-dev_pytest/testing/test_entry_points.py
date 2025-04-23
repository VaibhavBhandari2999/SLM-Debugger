import importlib_metadata


def test_pytest_entry_points_are_identical():
    """
    Tests if the entry points 'pytest' and 'py.test' in the 'pytest' distribution are identical.
    
    This function imports the 'pytest' distribution and retrieves its entry points. It then checks if the values of the entry points named 'pytest' and 'py.test' are identical.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    None
    
    Note:
    The function uses the `importlib_metadata` module to work with distribution entry points.
    """

    dist = importlib_metadata.distribution("pytest")
    entry_map = {ep.name: ep for ep in dist.entry_points}
    assert entry_map["pytest"].value == entry_map["py.test"].value
