import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function customizes the collection of test modules in pytest. It checks if the test file's basename contains 'py3' and the Python version is not 3, or if the basename contains 'py2' and the Python version is 3. If either condition is met, it returns a DummyCollector instance to skip collecting that specific test module. The function takes two parameters: `path` representing the test file path and `parent` representing the parent collection object.
    
    Parameters:
    - path (
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
