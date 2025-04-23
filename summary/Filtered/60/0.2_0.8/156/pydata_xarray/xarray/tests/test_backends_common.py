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
        
        This method is used to simulate a behavior where accessing an item from the object may fail a certain number of times before succeeding.
        """

        if self.failures:
            self.failures -= 1
            raise DummyFailure
        return "success"


def test_robust_getitem():
    """
    Robustly retrieve an item from an array, handling specified exceptions.
    
    This function attempts to retrieve an item from the given array using the specified
    index. If a specified exception (DummyFailure) is raised, it will be caught and
    the function will retry the operation with an increasing delay between attempts.
    
    Parameters:
    array (object): The array-like object from which to retrieve the item.
    index (object): The index to use for retrieving the item from the array.
    catch (Exception
    """

    array = DummyArray(failures=2)
    with pytest.raises(DummyFailure):
        array[...]
    result = robust_getitem(array, ..., catch=DummyFailure, initial_delay=1)
    assert result == "success"

    array = DummyArray(failures=3)
    with pytest.raises(DummyFailure):
        robust_getitem(array, ..., catch=DummyFailure, initial_delay=1, max_retries=2)
