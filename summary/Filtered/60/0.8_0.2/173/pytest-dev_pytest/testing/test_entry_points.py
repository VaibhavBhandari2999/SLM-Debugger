import importlib_metadata


def test_pytest_entry_points_are_identical():
    """
    Test that the entry points 'pytest' and 'py.test' in the 'pytest' distribution are identical.
    
    This function checks the distribution of 'pytest' using importlib_metadata and compares the entry points 'pytest' and 'py.test'. It returns True if they are identical, and False otherwise.
    
    Parameters:
    None
    
    Returns:
    bool: True if the entry points 'pytest' and 'py.test' are identical, False otherwise.
    """

    dist = importlib_metadata.distribution("pytest")
    entry_map = {ep.name: ep for ep in dist.entry_points}
    assert entry_map["pytest"].value == entry_map["py.test"].value
