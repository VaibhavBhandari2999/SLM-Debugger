import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to run before each test function in a Pytest test suite. It checks if the test function is part of a specific directory (mydir) and if the module associated with the test function has a method named 'hello'. If both conditions are met, it prints a message containing the value of 'mod.hello'.
    
    Parameters:
    - item: The test function or module being executed. It is an instance of pytest.Function or pytest.Module.
    
    Returns
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
