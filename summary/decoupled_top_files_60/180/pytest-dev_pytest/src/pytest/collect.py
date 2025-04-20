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
        
        This method initializes the pytest.collect module, setting up the necessary attributes and dependencies. It inherits from a superclass and initializes the module with a specific name. Additionally, it sets the `__all__` attribute to a list of attributes from `COLLECT_FAKEMODULE_ATTRIBUTES` and assigns `pytest` to the `__pytest` attribute.
        
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
        Retrieve an attribute from the pytest module.
        
        This method is called when an attribute of the current object is accessed and not found in the object's dictionary. If the attribute is not in the predefined list `__all__`, an `AttributeError` is raised. Otherwise, a warning is issued using the `warnings.warn` function, and the attribute is retrieved from the `pytest` module using `getattr`.
        
        Parameters:
        name (str): The name of the attribute to retrieve.
        
        Returns:
        Any
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
