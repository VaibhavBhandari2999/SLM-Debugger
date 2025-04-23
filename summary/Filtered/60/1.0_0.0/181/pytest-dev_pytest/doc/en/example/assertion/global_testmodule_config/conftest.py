import os.path

import pytest

mydir = os.path.dirname(__file__)


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is a pytest hook that runs before a test function is executed. It checks if the test function is located within a specific directory (`mydir`). If the test function is within this directory, it retrieves the module object associated with the test file and checks if the module has an attribute named `hello`. If the attribute exists, it prints its value.
    
    Parameters:
    - item (pytest.Function): The test function that is about to be executed.
    
    Returns:
    -
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print(f"mod.hello {mod.hello!r}")
