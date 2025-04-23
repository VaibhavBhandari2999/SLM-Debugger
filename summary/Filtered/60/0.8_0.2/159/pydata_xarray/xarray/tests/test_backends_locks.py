import threading

from xarray.backends import locks


def test_threaded_lock():
    """
    Test function for thread-safe locking mechanism.
    
    This function checks the behavior of the thread-safe locking mechanism by creating locks with specific names and verifying that locks with the same name are the same object, while locks with different names are distinct objects.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `lock1`: A thread-safe lock with the name "foo".
    - `lock2`: Another thread-safe lock with the name "foo". Should be the same object as `lock
    """

    lock1 = locks._get_threaded_lock("foo")
    assert isinstance(lock1, type(threading.Lock()))
    lock2 = locks._get_threaded_lock("foo")
    assert lock1 is lock2

    lock3 = locks._get_threaded_lock("bar")
    assert lock1 is not lock3
