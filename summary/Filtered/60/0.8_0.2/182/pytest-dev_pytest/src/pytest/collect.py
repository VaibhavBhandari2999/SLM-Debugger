import sys
import warnings
from types import ModuleType
from typing import Any
from typing import List

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
    def __init__(self) -> None:
        """
        Initialize the pytest.collect module.
        
        This method initializes the pytest.collect module and sets up the necessary attributes and dependencies.
        
        Parameters:
        None
        
        Returns:
        None
        """

        super().__init__("pytest.collect")
        self.__all__ = list(COLLECT_FAKEMODULE_ATTRIBUTES)
        self.__pytest = pytest

    def __dir__(self) -> List[str]:
        return dir(super()) + self.__all__

    def __getattr__(self, name: str) -> Any:
        """
        Summary:
        This method handles attribute access for a custom object. It checks if the requested attribute is in the predefined list of attributes (__all__). If the attribute is not found, it raises an AttributeError. Otherwise, it issues a warning and returns the attribute from the pytest module.
        
        Parameters:
        name (str): The name of the attribute being accessed.
        
        Returns:
        Any: The value of the attribute from the pytest module, or raises an AttributeError if the attribute is not found in __all__.
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
