import pytest

from xarray.backends.common import robust_getitem


class DummyFailure(Exception):
    pass


class DummyArray:
    def __init__(self, failures):
        self.failures = failures

    def __getitem__(self, key):
        """
        __getitem__(self, key)
        
        Parameters:
        - key: The key used to access an item in the object.
        
        Returns:
        - "success": If no failures are pending, the function returns "success".
        - DummyFailure: If there are pending failures, the function raises a DummyFailure exception and decreases the failure count by one.
        
        This method is used to simulate a get-item operation where the object can fail a certain number of times before succeeding.
        """

        if self.failures:
            self.failures -= 1
            raise DummyFailure
        return "success"


def test_robust_getitem():
    array = DummyArray(failures=2)
    with pytest.raises(DummyFailure):
        array[...]
    result = robust_getitem(array, ..., catch=DummyFailure, initial_delay=1)
    assert result == "success"

    array = DummyArray(failures=3)
    with pytest.raises(DummyFailure):
        robust_getitem(array, ..., catch=DummyFailure, initial_delay=1, max_retries=2)
1, max_retries=2)
