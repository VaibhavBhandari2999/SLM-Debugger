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
        Initialize the collect module.
        
        This method initializes the collect module with the specified name and sets the `__all__` attribute to a list of attributes from the `COLLECT_FAKEMODULE_ATTRIBUTES` constant. It also assigns the `pytest` module to the `__pytest` attribute.
        
        Args:
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
        Retrieve an attribute from the `pytest` module.
        
        This method is called when an attribute of the test collection object
        that is not defined locally is accessed. If the attribute does not exist
        in the predefined list of attributes (`self.__all__`), an `AttributeError`
        is raised. Otherwise, a warning is issued using the `warnings.warn`
        function with a specific message indicating the attribute being accessed,
        and the corresponding attribute from the `pytest` module is returned
        """

        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
