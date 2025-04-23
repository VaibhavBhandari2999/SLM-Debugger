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
        Initialize the pytest.collect module.
        
        This method initializes the pytest.collect module, setting up the necessary attributes and configurations. It inherits from a superclass and assigns a specific name. Additionally, it populates the `__all__` attribute with a predefined list of attributes and imports `pytest`.
        
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
        Docstring for __getattr__ method:
        
        This method is a custom implementation of the __getattr__ magic method, which is used to handle attribute access in Python classes. It is designed to intercept attribute access for attributes not explicitly defined in the class.
        
        Parameters:
        name (str): The name of the attribute being accessed.
        
        Returns:
        object: The value of the attribute if it exists in the pytest module, otherwise raises an AttributeError.
        
        Raises:
        AttributeError: If the attribute name is not in the
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
