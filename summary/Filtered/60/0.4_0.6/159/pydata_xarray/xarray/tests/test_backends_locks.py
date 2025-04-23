import threading

from xarray.backends import locks


def test_threaded_lock():
    """
    Test a threaded lock.
    
    This function checks the behavior of a threaded lock by creating multiple locks with the same name and different names. It ensures that locks with the same name are the same object, while locks with different names are different objects.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `lock1`: A threaded lock with the name "foo".
    - `lock2`: Another threaded lock with the name "foo". This should be the same object as `lock
    """

    lock1 = locks._get_threaded_lock("foo")
    assert isinstance(lock1, type(threading.Lock()))
    lock2 = locks._get_threaded_lock("foo")
    assert lock1 is lock2

    lock3 = locks._get_threaded_lock("bar")
    assert lock1 is not lock3
