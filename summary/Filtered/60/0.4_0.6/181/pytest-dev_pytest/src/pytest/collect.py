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
        super().__init__("pytest.collect")
        self.__all__ = list(COLLECT_FAKEMODULE_ATTRIBUTES)
        self.__pytest = pytest

    def __dir__(self) -> List[str]:
        return dir(super()) + self.__all__

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the pytest module.
        
        This method is called when an attribute that is not defined in the current class is accessed. If the attribute is not in the predefined list `__all__`, an `AttributeError` is raised. Otherwise, a warning is issued using the `warnings` module, and the attribute is retrieved from the `pytest` module.
        
        Parameters:
        name (str): The name of the attribute to be accessed.
        
        Returns:
        Any: The value of the attribute from
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
