from unittest import mock

import pytest

from xarray.backends.lru_cache import LRUCache


def test_simple():
    """
    Test the functionality of a simple LRUCache.
    
    This function tests the LRUCache class with a maxsize of 2. It checks the following:
    - Setting and retrieving values.
    - The length of the cache.
    - Conversion to a dictionary.
    - Retrieval of keys and items.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Assertions:
    - The value of 'x' is 1.
    - The value of 'y' is 2.
    - The length of the cache is
    """

    cache = LRUCache(maxsize=2)
    cache["x"] = 1
    cache["y"] = 2

    assert cache["x"] == 1
    assert cache["y"] == 2
    assert len(cache) == 2
    assert dict(cache) == {"x": 1, "y": 2}
    assert list(cache.keys()) == ["x", "y"]
    assert list(cache.items()) == [("x", 1), ("y", 2)]

    cache["z"] = 3
    assert len(cache) == 2
    assert list(cache.items()) == [("y", 2), ("z", 3)]


def test_trivial():
    cache = LRUCache(maxsize=0)
    cache["x"] = 1
    assert len(cache) == 0


def test_invalid():
    with pytest.raises(TypeError):
        LRUCache(maxsize=None)
    with pytest.raises(ValueError):
        LRUCache(maxsize=-1)


def test_update_priority():
    cache = LRUCache(maxsize=2)
    cache["x"] = 1
    cache["y"] = 2
    assert list(cache) == ["x", "y"]
    assert "x" in cache  # contains
    assert list(cache) == ["y", "x"]
    assert cache["y"] == 2  # getitem
    assert list(cache) == ["x", "y"]
    cache["x"] = 3  # setitem
    assert list(cache.items()) == [("y", 2), ("x", 3)]


def test_del():
    cache = LRUCache(maxsize=2)
    cache["x"] = 1
    cache["y"] = 2
    del cache["x"]
    assert dict(cache) == {"y": 2}


def test_on_evict():
    on_evict = mock.Mock()
    cache = LRUCache(maxsize=1, on_evict=on_evict)
    cache["x"] = 1
    cache["y"] = 2
    on_evict.assert_called_once_with("x", 1)


def test_on_evict_trivial():
    """
    Function to test the on_evict callback in an LRUCache.
    
    This function creates an LRUCache with a maximum size of 0 and a custom on_evict callback. It then adds a key-value pair to the cache and checks if the on_evict callback is called with the correct arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - on_evict: A mock object representing the on_evict callback function.
    
    Keywords:
    - maxsize: The maximum
    """

    on_evict = mock.Mock()
    cache = LRUCache(maxsize=0, on_evict=on_evict)
    cache["x"] = 1
    on_evict.assert_called_once_with("x", 1)


def test_resize():
    cache = LRUCache(maxsize=2)
    assert cache.maxsize == 2
    cache["w"] = 0
    cache["x"] = 1
    cache["y"] = 2
    assert list(cache.items()) == [("x", 1), ("y", 2)]
    cache.maxsize = 10
    cache["z"] = 3
    assert list(cache.items()) == [("x", 1), ("y", 2), ("z", 3)]
    cache.maxsize = 1
    assert list(cache.items()) == [("z", 3)]

    with pytest.raises(ValueError):
        cache.maxsize = -1
z", 3)]

    with pytest.raises(ValueError):
        cache.maxsize = -1
