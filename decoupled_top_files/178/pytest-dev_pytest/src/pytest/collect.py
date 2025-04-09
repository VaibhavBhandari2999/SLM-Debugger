import sys
import warnings
from types import ModuleType

import pytest
from _pytest.deprecated import PYTEST_COLLECT_MODULE


COLLECT_FAKEMODULE_ATTRIBUTES = [
    "Collector",
    "Module",
    "Function",
    "Instance",
    "Session",
    "Item",
    "Class",
    "File",
    "_fillfuncargs",
]


class FakeCollectModule(ModuleType):
    def __init__(self):
        """
        Initialize the collect object with the specified pytest module and set the __all__ attribute to a list of COLLECT_FAKEMODULE_ATTRIBUTES. The super() call initializes the object with the pytest.collect namespace. The __pytest attribute is assigned the pytest module.
        """

        super().__init__("pytest.collect")
        self.__all__ = list(COLLECT_FAKEMODULE_ATTRIBUTES)
        self.__pytest = pytest

    def __dir__(self):
        return dir(super()) + self.__all__

    def __getattr__(self, name):
        """
        Summary: This function is used to handle attribute access for a class instance. If the requested attribute is not in the predefined list of attributes (__all__), an AttributeError is raised. Otherwise, a warning is issued using the `warnings` module with a specific message related to pytest collection, and the attribute is then retrieved from the `pytest` module.
        
        Args:
        name (str): The name of the attribute being accessed.
        
        Raises:
        AttributeError: If the attribute is not in the predefined list
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
