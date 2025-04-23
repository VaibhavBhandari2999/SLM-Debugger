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
        
        This method initializes the pytest.collect module and sets up the necessary attributes. It inherits from a superclass using the provided name "pytest.collect". The module also includes a list of attributes defined in `COLLECT_FAKEMODULE_ATTRIBUTES` and a reference to the pytest module.
        
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
        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
