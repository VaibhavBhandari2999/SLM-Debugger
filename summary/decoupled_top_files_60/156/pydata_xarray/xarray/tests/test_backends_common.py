import pytest

from xarray.backends.common import robust_getitem


class DummyFailure(Exception):
    pass


class DummyArray:
    def __init__(self, failures):
        self.failures = failures

    def __getitem__(self, key):
        if self.failures:
            self.failures -= 1
            raise DummyFailure
        return "success"


def test_robust_getitem():
    """
    Robustly retrieve an item from an array, handling failures gracefully.
    
    This function attempts to retrieve an item from the given array. If a failure
    occurs, it retries the operation with an increasing delay between attempts,
    up to a maximum number of retries. The function can catch specific types of
    failures and handle them according to the provided parameters.
    
    Parameters:
    array (object): The array-like object from which to retrieve the item.
    index (object): The index or slice to use
    """

    array = DummyArray(failures=2)
    with pytest.raises(DummyFailure):
        array[...]
    result = robust_getitem(array, ..., catch=DummyFailure, initial_delay=1)
    assert result == "success"

    array = DummyArray(failures=3)
    with pytest.raises(DummyFailure):
        robust_getitem(array, ..., catch=DummyFailure, initial_delay=1, max_retries=2)
