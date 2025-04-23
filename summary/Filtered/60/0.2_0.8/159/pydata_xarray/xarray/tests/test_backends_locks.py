import threading

from xarray.backends import locks


def test_threaded_lock():
    """
    Test function for thread-safe locking mechanism.
    
    This function checks the behavior of the thread-safe locking mechanism. It ensures that locks are created in a thread-safe manner and that locks for the same key are shared across different calls.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A lock is created for a given key.
    - Locks for the same key are the same object.
    - Locks for different keys are different objects.
    """

    lock1 = locks._get_threaded_lock("foo")
    assert isinstance(lock1, type(threading.Lock()))
    lock2 = locks._get_threaded_lock("foo")
    assert lock1 is lock2

    lock3 = locks._get_threaded_lock("bar")
    assert lock1 is not lock3
