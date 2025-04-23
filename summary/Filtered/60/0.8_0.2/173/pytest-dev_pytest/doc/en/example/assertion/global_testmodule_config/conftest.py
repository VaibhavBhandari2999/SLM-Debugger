import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to be used as a setup hook for pytest tests. It is executed before each test function is run.
    
    Parameters:
    - item (pytest.Function): The test function that is about to be executed.
    
    Returns:
    - None: This function does not return any value. It is intended to modify the behavior of the test setup process.
    
    Behavior:
    - It checks if the test function is part of a module that is located in a specific directory (`mydir
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
