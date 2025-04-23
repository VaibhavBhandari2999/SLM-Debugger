import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that filters test modules based on Python version compatibility. It checks if the test module's basename contains 'py3' or 'py2' and ensures it matches the current Python version being used. If the module is not compatible with the current Python version, it returns a DummyCollector instance to skip that test module.
    
    Parameters:
    - path (pytest.path): The path to the test module.
    - parent (pytest.Fixture): The parent collector.
    
    Returns:
    -
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
