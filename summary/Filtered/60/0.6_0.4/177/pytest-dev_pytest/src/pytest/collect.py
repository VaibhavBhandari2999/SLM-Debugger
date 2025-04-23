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
        
        This method initializes the pytest.collect module, setting up a super class with the specified name and populating the __all__ attribute with a list of attributes from COLLECT_FAKEMODULE_ATTRIBUTES. Additionally, it assigns pytest to the __pytest attribute.
        
        Parameters:
        - None
        
        Attributes Set:
        - __all__: A list of attributes from COLLECT_FAKEMODULE_ATTRIBUTES.
        - __pytest: The pytest module.
        
        Returns:
        - None
        """

        super().__init__("pytest.collect")
        self.__all__ = list(COLLECT_FAKEMODULE_ATTRIBUTES)
        self.__pytest = pytest

    def __dir__(self):
        return dir(super()) + self.__all__

    def __getattr__(self, name):
        if name not in self.__all__:
            raise AttributeError(name)
        warnings.warn(PYTEST_COLLECT_MODULE.format(name=name), stacklevel=2)
        return getattr(pytest, name)


sys.modules["pytest.collect"] = FakeCollectModule()
