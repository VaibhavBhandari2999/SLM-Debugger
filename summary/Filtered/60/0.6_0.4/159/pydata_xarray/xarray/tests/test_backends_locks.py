import threading

from xarray.backends import locks


def test_threaded_lock():
    """
    Test function for thread-safe locking mechanism.
    
    This function checks the behavior of the thread-safe locking mechanism by creating locks for different keys and ensuring that locks for the same key are the same instance.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Creates a lock for a specific key ("foo").
    - Verifies that the lock for the same key ("foo") is the same instance.
    - Creates a lock for a different key ("bar").
    - Verifies that the
    """

    lock1 = locks._get_threaded_lock("foo")
    assert isinstance(lock1, type(threading.Lock()))
    lock2 = locks._get_threaded_lock("foo")
    assert lock1 is lock2

    lock3 = locks._get_threaded_lock("bar")
    assert lock1 is not lock3
