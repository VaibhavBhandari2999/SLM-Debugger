import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to be used as a hook function in the pytest framework. It is called before a test function is executed.
    
    Parameters:
    - item (pytest.Function): The test function that is about to be executed.
    
    Returns:
    - None: This function does not return any value. It is used for side effects such as setting up the test environment.
    
    Notes:
    - The function checks if the test function is located in a specific directory (`mydir`). If
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
