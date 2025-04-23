from collections import Mapping, MutableMapping
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
from .packages.six import itervalues


__all__ = ['RecentlyUsedContainer', 'HTTPHeaderDict']


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
        self._maxsize = maxsize
        self.dispose_func = dispose_func

        self._container = self.ContainerCls()
        self.lock = RLock()

    def __getitem__(self, key):
        """
        Retrieve an item from the cache.
        
        This method retrieves an item from the cache using the specified key. The item is then re-inserted into the cache, moving it to the end of the eviction line to reflect its recent access.
        
        Parameters:
        key (Any): The key used to identify the item in the cache.
        
        Returns:
        Any: The item associated with the given key.
        
        Raises:
        KeyError: If the key is not found in the cache.
        
        Note:
        The method uses a lock
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
        Clears the internal container of all stored values.
        
        This method acquires a lock to ensure thread safety, then copies the list of values from the container and clears the container itself. After clearing, it disposes of each value using the provided dispose function if one is defined.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        _container (dict): The internal dictionary storing the values.
        lock (threading.Lock): The lock used to ensure thread safety.
        dispose_func (function
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


class HTTPHeaderDict(MutableMapping):
    """
    :param headers:
        An iterable of field-value pairs. Must not contain multiple field names
        when compared case-insensitively.

    :param kwargs:
        Additional field-value pairs to pass in to ``dict.update``.

    A ``dict`` like container for storing HTTP Headers.

    Field names are stored and compared case-insensitively in compliance with
    RFC 7230. Iteration provides the first case-sensitive key seen for each
    case-insensitive pair.

    Using ``__setitem__`` syntax overwrites fields that compare equal
    case-insensitively in order to maintain ``dict``'s api. For fields that
    compare equal, instead create a new ``HTTPHeaderDict`` and use ``.add``
    in a loop.

    If multiple fields that are equal case-insensitively are passed to the
    constructor or ``.update``, the behavior is undefined and some will be
    lost.

    >>> headers = HTTPHeaderDict()
    >>> headers.add('Set-Cookie', 'foo=bar')
    >>> headers.add('set-cookie', 'baz=quxx')
    >>> headers['content-length'] = '7'
    >>> headers['SET-cookie']
    'foo=bar, baz=quxx'
    >>> headers['Content-Length']
    '7'

    If you want to access the raw headers with their original casing
    for debugging purposes you can access the private ``._data`` attribute
    which is a normal python ``dict`` that maps the case-insensitive key to a
    list of tuples stored as (case-sensitive-original-name, value). Using the
    structure from above as our example:

    >>> headers._data
    {'set-cookie': [('Set-Cookie', 'foo=bar'), ('set-cookie', 'baz=quxx')],
    'content-length': [('content-length', '7')]}
    """

    def __init__(self, headers=None, **kwargs):
        """
        Initialize a new instance of the class.
        
        Args:
        headers (dict, optional): A dictionary of headers to initialize the instance with. Defaults to an empty dictionary if not provided.
        **kwargs: Additional keyword arguments to update the instance with.
        
        This method initializes a new instance of the class with an empty data dictionary. If headers are provided, they are used to initialize the instance. The headers argument can be a dictionary or omitted if no headers are needed. Additional keyword arguments can be passed to further
        """

        self._data = {}
        if headers is None:
            headers = {}
        self.update(headers, **kwargs)

    def add(self, key, value):
        """Adds a (name, value) pair, doesn't overwrite the value if it already
        exists.

        >>> headers = HTTPHeaderDict(foo='bar')
        >>> headers.add('Foo', 'baz')
        >>> headers['foo']
        'bar, baz'
        """
        self._data.setdefault(key.lower(), []).append((key, value))

    def getlist(self, key):
        """Returns a list of all the values for the named field. Returns an
        empty list if the key doesn't exist."""
        return self[key].split(', ') if key in self else []

    def copy(self):
        """
        Copy the HTTPHeaderDict object.
        
        This method creates a shallow copy of the current HTTPHeaderDict object. Each key-value pair in the original dictionary is added to the new object. The new object maintains the same structure and content as the original.
        
        Parameters:
        None
        
        Returns:
        HTTPHeaderDict: A new instance of HTTPHeaderDict that is a shallow copy of the original object.
        
        Example:
        >>> original_headers = HTTPHeaderDict()
        >>> original_headers.add('Content-Type', 'application
        """

        h = HTTPHeaderDict()
        for key in self._data:
            for rawkey, value in self._data[key]:
                h.add(rawkey, value)
        return h

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return False
        other = HTTPHeaderDict(other)
        return dict((k1, self[k1]) for k1 in self._data) == \
                dict((k2, other[k2]) for k2 in other._data)

    def __getitem__(self, key):
        values = self._data[key.lower()]
        return ', '.join(value[1] for value in values)

    def __setitem__(self, key, value):
        self._data[key.lower()] = [(key, value)]

    def __delitem__(self, key):
        del self._data[key.lower()]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for headers in itervalues(self._data):
            yield headers[0][0]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))
elf.items()))
