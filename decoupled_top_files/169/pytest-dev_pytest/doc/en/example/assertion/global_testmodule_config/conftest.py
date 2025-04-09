import py

import pytest

mydir = py.path.local(__file__).dirpath()


def pytest_runtest_setup(item):
    """
    pytest_runtest_setup is a hook function that runs before each test function in a pytest session. It checks if the test function is an instance of pytest.Function and if its file path is within a specific directory (mydir). If both conditions are met, it retrieves the module object associated with the test function and checks if it has a 'hello' attribute. If the 'hello' attribute exists, it prints the value of the attribute.
    
    Args:
    item (pytest.Function): The test function
    """

    if isinstance(item, pytest.Function):
        if not item.fspath.relto(mydir):
            return
        mod = item.getparent(pytest.Module).obj
        if hasattr(mod, "hello"):
            print("mod.hello {!r}".format(mod.hello))
