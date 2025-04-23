import os.path

import pytest

mydir = os.path.dirname(__file__)


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    This function is designed to be used as a hook function in pytest. It is called before a test function is executed. The function checks if the test function is part of a specific directory (mydir) and if the module associated with the test function has a method named 'hello'. If both conditions are met, it prints the value of 'mod.hello'.
    
    Parameters:
    - item: The test item to be executed. It is expected to be a pytest.Function
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print(f"mod.hello {mod.hello!r}")
