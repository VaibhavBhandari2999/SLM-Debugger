import os.path

import pytest

mydir = os.path.dirname(__file__)


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is a pytest hook that is called before each test function is executed.
    
    Parameters:
    - item (pytest.Function): The test function that is about to be executed.
    
    Returns:
    - None: This function does not return a value. It is used to perform setup actions before a test function runs.
    
    Notes:
    - The function checks if the test function is located in a specific directory (mydir).
    - If the test function is in the specified directory, it retrieves
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print(f"mod.hello {mod.hello!r}")
