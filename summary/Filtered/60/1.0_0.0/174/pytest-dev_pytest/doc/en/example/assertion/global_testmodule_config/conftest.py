import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to be used as a hook function in the pytest framework. It is called during the setup phase of a test to perform specific actions based on the test function or module being executed.
    
    Parameters:
    - item (pytest.Function or pytest.Module): The test item (function or module) being set up.
    
    Returns:
    - None: This function does not return a value. It is intended to modify the behavior of the test setup process.
    
    Notes:
    - The
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
