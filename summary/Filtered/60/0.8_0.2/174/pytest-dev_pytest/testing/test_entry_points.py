from _pytest.compat import importlib_metadata


def test_pytest_entry_points_are_identical():
    """
    Test that the entry points 'pytest' and 'py.test' in the 'pytest' distribution are identical.
    
    This function checks the distribution of 'pytest' and retrieves its entry points. It then creates a dictionary of these entry points, using the names as keys. The function asserts that the values (the entry points themselves) for 'pytest' and 'py.test' are identical.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the entry points for 'pytest'
    """

    dist = importlib_metadata.distribution("pytest")
    entry_map = {ep.name: ep for ep in dist.entry_points}
    assert entry_map["pytest"].value == entry_map["py.test"].value
