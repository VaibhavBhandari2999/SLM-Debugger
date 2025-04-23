import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is used to set up a test case in the pytest framework. It is called before each test function is executed.
    
    Parameters:
    - item: The test item to be set up. This is typically a pytest function or module.
    
    Returns:
    - None
    
    Notes:
    - This function checks if the test item is a function and if it is located in a specific directory (mydir).
    - If the test item is a function and it is located in the specified
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
