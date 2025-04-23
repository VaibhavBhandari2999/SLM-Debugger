import sys

import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    """
    This function is a custom collector for pytest that filters test modules based on Python version compatibility. It checks if the test module's basename contains 'py3' and the current Python version is not 3, or if the basename contains 'py2' and the current Python version is 3. If either condition is met, it returns a DummyCollector instance, effectively skipping the collection of that test module.
    
    Parameters:
    - path (Path): The path to the test module.
    - parent (Collector):
    """

    bn = path.basename
    if "py3" in bn and not py3 or ("py2" in bn and py3):
        return DummyCollector(path, parent=parent)
