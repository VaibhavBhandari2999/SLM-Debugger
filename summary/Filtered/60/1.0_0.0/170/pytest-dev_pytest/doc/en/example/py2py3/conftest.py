import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that modifies the collection process based on the filename and the Python version being used. It checks if the filename contains 'py3' and the Python version is not 3, or if the filename contains 'py2' and the Python version is 3. If either condition is met, it returns a DummyCollector instance, otherwise, it returns None.
    
    Parameters:
    - path: The path object representing the file to be collected.
    - parent: The parent collector
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
