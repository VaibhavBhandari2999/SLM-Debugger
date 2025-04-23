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
        Initialize the pytest.collect object.
        
        This method initializes the pytest.collect object by calling the superclass initializer with the argument "pytest.collect". It also sets the `__all__` attribute to a list of attributes from `COLLECT_FAKEMODULE_ATTRIBUTES` and assigns `pytest` to the `__pytest` attribute.
        
        Parameters:
        None
        
        Returns:
        None
        """

        super().__init__("pytest.collect")
        self.__all__ = list(COLLECT_FAKEMODULE_ATTRIBUTES)
        self.__pytest = pytest

    def __dir__(self):
        return dir(super()) + self.__all__

    def __getattr__(self, name):
        """
        Summary:
        This method is a custom implementation of the `__getattr__` method, which is used to handle attribute access in a class. If the attribute being accessed is not in the predefined list `__all__`, it raises an `AttributeError`. Otherwise, it issues a warning and returns the attribute from the `pytest` module.
        
        Parameters:
        - name (str): The name of the attribute being accessed.
        
        Returns:
        - The value of the attribute from the `pytest` module if it
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
