import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that modifies the collection process based on the Python version. It checks if the file name contains 'py3' or 'py2' and whether the current Python version is 3 or 2. If the file name and Python version do not match, it returns a DummyCollector to skip the collection of that module. The function takes two parameters:
    - `path`: The file path object representing the file to be collected.
    - `parent`: The parent collector
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
