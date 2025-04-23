# urllib3/_collections.py
# Copyright 2008-2013 Andrey Petrov and contributors (see CONTRIBUTORS.txt)
#
# This module is part of urllib3 and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from collections import MutableMapping
try:
    from threading import RLock
except ImportError: # Platform-specific: No threads available
    class RLock:
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            pass


try: # Python 2.7+
    from collections import OrderedDict
except ImportError:
    from .packages.ordered_dict import OrderedDict


__all__ = ['RecentlyUsedContainer']


_Null = object()


class RecentlyUsedContainer(MutableMapping):
    """
    Provides a thread-safe dict-like container which maintains up to
    ``maxsize`` keys while throwing away the least-recently-used keys beyond
    ``maxsize``.

    :param maxsize:
        Maximum number of recent elements to retain.

    :param dispose_func:
        Every time an item is evicted from the container,
        ``dispose_func(value)`` is called.  Callback which will get called
    """

    ContainerCls = OrderedDict

    def __init__(self, maxsize=10, dispose_func=None):
        """
        Initialize a container with a specified maximum size and an optional dispose function.
        
        Args:
        maxsize (int): The maximum number of items the container can hold. Default is 10.
        dispose_func (callable, optional): A function to call when an item is removed from the container. The function should accept one argument, the item to be disposed.
        
        Attributes:
        _maxsize (int): The maximum size of the container.
        dispose_func (callable): The dispose function to be called
        """

        self._maxsize = maxsize
        self.dispose_func = dispose_func

        self._container = self.ContainerCls()
        self.lock = RLock()

    def __getitem__(self, key):
        """
        Retrieve an item from the cache.
        
        This method retrieves an item from the cache using the provided key. The item is then re-inserted into the cache, moving it to the end of the eviction line.
        
        Parameters:
        key (Hashable): The key used to identify the item in the cache.
        
        Returns:
        Any: The item associated with the given key.
        
        Raises:
        KeyError: If the key is not found in the cache.
        
        Note:
        The method acquires a lock to ensure thread
        """

        # Re-insert the item, moving it to the end of the eviction line.
        with self.lock:
            item = self._container.pop(key)
            self._container[key] = item
            return item

    def __setitem__(self, key, value):
        evicted_value = _Null
        with self.lock:
            # Possibly evict the existing value of 'key'
            evicted_value = self._container.get(key, _Null)
            self._container[key] = value

            # If we didn't evict an existing value, we might have to evict the
            # least recently used item from the beginning of the container.
            if len(self._container) > self._maxsize:
                _key, evicted_value = self._container.popitem(last=False)

        if self.dispose_func and evicted_value is not _Null:
            self.dispose_func(evicted_value)

    def __delitem__(self, key):
        with self.lock:
            value = self._container.pop(key)

        if self.dispose_func:
            self.dispose_func(value)

    def __len__(self):
        with self.lock:
            return len(self._container)

    def __iter__(self):
        raise NotImplementedError('Iteration over this class is unlikely to be threadsafe.')

    def clear(self):
        """
        Clears the internal container and disposes of all stored values.
        
        This method acquires a lock to ensure thread safety, then copies the list of values from the container. It then clears the internal container. After that, it iterates over the copied list of values and disposes of each value using the provided dispose function.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        _container (dict): The internal dictionary storing the values.
        lock (threading.Lock): The lock used
        """

        with self.lock:
            # Copy pointers to all values, then wipe the mapping
            # under Python 2, this copies the list of values twice :-|
            values = list(self._container.values())
            self._container.clear()

        if self.dispose_func:
            for value in values:
                self.dispose_func(value)

    def keys(self):
        with self.lock:
            return self._container.keys()
