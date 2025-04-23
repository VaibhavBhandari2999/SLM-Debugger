import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is designed to be used as a hook function in pytest, which is a popular testing framework for Python. It is specifically called during the setup phase of a test function.
    
    Parameters:
    - item: The item to be tested. In this case, it is expected to be a pytest.Function object, which represents a single test function.
    
    Returns:
    - None: This function does not return any value. It is intended to perform side effects such as modifying the test
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
