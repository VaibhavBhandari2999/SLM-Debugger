from unittest import mock

import pytest

from xarray.backends.lru_cache import LRUCache


def test_simple():
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
    """
    Function to test a trivial case of an LRUCache with maxsize set to 0.
    
    Parameters:
    None
    
    Returns:
    None
    
    This function creates an LRUCache with a maximum size of 0, attempts to add a key-value pair to it, and then asserts that the cache size is still 0, demonstrating that no items can be stored in an LRUCache with maxsize 0.
    """

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
 assert list(cache.items()) == [("z", 3)]

    with pytest.raises(ValueError):
        cache.maxsize = -1
