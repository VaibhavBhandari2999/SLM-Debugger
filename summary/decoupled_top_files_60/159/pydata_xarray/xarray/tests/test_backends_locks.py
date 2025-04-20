import threading

from xarray.backends import locks


def test_threaded_lock():
    """
    Test a threaded lock mechanism.
    
    This function checks the behavior of a threaded lock mechanism by creating multiple locks with the same and different names.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `lock1`: A lock with the name "foo".
    - `lock2`: Another lock with the name "foo". This should be the same instance as `lock1`.
    - `lock3`: A lock with the name "bar". This should be a different instance from
    """

    lock1 = locks._get_threaded_lock("foo")
    assert isinstance(lock1, type(threading.Lock()))
    lock2 = locks._get_threaded_lock("foo")
    assert lock1 is lock2

    lock3 = locks._get_threaded_lock("bar")
    assert lock1 is not lock3
