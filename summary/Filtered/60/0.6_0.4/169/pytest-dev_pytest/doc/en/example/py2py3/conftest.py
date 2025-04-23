import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that modifies the module collection process based on the filename. It checks if the filename contains 'py3' and the Python version is not 3, or if the filename contains 'py2' and the Python version is 3. If either condition is met, it returns a `DummyCollector` to skip the module collection for that specific file. The function takes two parameters:
    - `path`: The path object representing the file to be collected.
    - `
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
