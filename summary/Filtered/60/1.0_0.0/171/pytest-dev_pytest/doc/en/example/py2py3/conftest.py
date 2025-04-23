import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that selectively creates test modules based on the Python version. It checks if the test file name contains 'py3' and the current Python version is not 3, or if the file name contains 'py2' and the current Python version is 3. If either condition is met, it returns a DummyCollector instance, otherwise, it proceeds to create the test module as usual.
    
    Parameters:
    - path: The path to the test file.
    - parent:
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
