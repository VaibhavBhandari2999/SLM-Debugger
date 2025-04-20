import os.path

import pytest

mydir = os.path.dirname(__file__)


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to be used as a pytest hook to run setup operations for test functions. It is triggered before a test function is executed.
    
    Parameters:
    - item (pytest.Function): The test function that is about to be executed.
    
    Returns:
    - None: This function does not return any value. It is intended to perform setup actions and print information.
    
    Notes:
    - The function checks if the test function is located within a specific directory (`mydir`).
    -
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print(f"mod.hello {mod.hello!r}")
