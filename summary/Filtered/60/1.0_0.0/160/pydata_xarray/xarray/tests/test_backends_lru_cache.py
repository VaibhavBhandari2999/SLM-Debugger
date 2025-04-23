from unittest import mock

import pytest

from xarray.backends.lru_cache import LRUCache


def test_simple():
    """
    Function to test the basic functionalities of an LRUCache.
    
    Parameters:
    None
    
    Returns:
    None
    
    This function tests the following functionalities of the LRUCache:
    - Setting and retrieving values.
    - Checking the length of the cache.
    - Converting the cache to a dictionary.
    - Retrieving keys and items from the cache.
    - Handling cache size limits and eviction of the least recently used items.
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
    """
    Function to test invalid inputs for LRUCache.
    
    This function checks for invalid inputs to the LRUCache constructor and raises appropriate exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If maxsize is not provided or is not an integer.
    ValueError: If maxsize is a negative integer.
    """

    with pytest.raises(TypeError):
        LRUCache(maxsize=None)
    with pytest.raises(ValueError):
        LRUCache(maxsize=-1)


def test_update_priority():
    """
    Tests the update_priority method of the LRUCache class.
    
    This function checks the behavior of the LRUCache class when updating the priority of items in the cache.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Steps:
    1. Initializes an LRUCache with a maximum size of 2.
    2. Adds two items "x" and "y" to the cache.
    3. Verifies that the cache contains the expected items in the correct order.
    4. Retrieves an item from the
    """

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
