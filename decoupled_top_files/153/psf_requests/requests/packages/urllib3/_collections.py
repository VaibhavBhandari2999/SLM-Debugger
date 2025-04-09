from collections import Mapping, MutableMapping
try:
    from threading import RLock
except ImportError:  # Platform-specific: No threads available
    class RLock:
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            pass


try:  # Python 2.7+
    from collections import OrderedDict
except ImportError:
    from .packages.ordered_dict import OrderedDict
from .packages.six import iterkeys, itervalues, PY3


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
        """
        Initialize a new instance of the class.
        
        Args:
        maxsize (int): The maximum size of the container.
        dispose_func (function): A function to call when an item is removed from the container.
        
        Attributes:
        _maxsize (int): The maximum size of the container.
        dispose_func (function): A function to call when an item is removed from the container.
        _container (ContainerCls): The container used to store items.
        lock (RLock): A
        """

        self._maxsize = maxsize
        self.dispose_func = dispose_func

        self._container = self.ContainerCls()
        self.lock = RLock()

    def __getitem__(self, key):
        """
        Retrieve an item from the container using the given key.
        
        Args:
        key (any hashable type): The key used to identify the item in the container.
        
        Returns:
        any: The item associated with the given key.
        
        Summary:
        This method retrieves an item from the container using the provided key. It first removes the item from its current position in the container using `pop`, then re-inserts the item at the end of the eviction line using `_container[key] = item
        """

        # Re-insert the item, moving it to the end of the eviction line.
        with self.lock:
            item = self._container.pop(key)
            self._container[key] = item
            return item

    def __setitem__(self, key, value):
        """
        Sets the value at the specified key in the cache.
        
        Args:
        key: The key to set the value for.
        value: The value to set.
        
        Returns:
        The previously stored value for the given key, or `_Null` if no value was present.
        
        Effects:
        - Modifies the internal state of the cache by setting the value for the given key.
        - May evict the least recently used item from the cache if the maximum size is exceeded.
        -
        """

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
        """
        Delete an item from the container.
        
        Args:
        key: The key of the item to be deleted.
        
        Returns:
        The value associated with the deleted key.
        
        Effects:
        - Removes the specified key-value pair from the container.
        - Acquires a lock before accessing the container to ensure thread safety.
        - Calls the `dispose_func` function on the removed value if it is not None.
        """

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
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This method clears the internal container by first copying all values using `itervalues` and then wiping the mapping with `clear`. If a dispose function is set, it will be called on each value using `self.dispose_func(value)`.
        
        Effects:
        - Modifies the internal state of the object by clearing its container.
        - Calls the `dispose_func`
        """

        with self.lock:
            # Copy pointers to all values, then wipe the mapping
            values = list(itervalues(self._container))
            self._container.clear()

        if self.dispose_func:
            for value in values:
                self.dispose_func(value)

    def keys(self):
        with self.lock:
            return list(iterkeys(self._container))


_dict_setitem = dict.__setitem__
_dict_getitem = dict.__getitem__
_dict_delitem = dict.__delitem__
_dict_contains = dict.__contains__
_dict_setdefault = dict.setdefault


class HTTPHeaderDict(dict):
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
    """

    def __init__(self, headers=None, **kwargs):
        """
        Initialize an instance of the HTTPHeaderDict class.
        
        Args:
        headers (HTTPHeaderDict or dict): A dictionary-like object containing HTTP headers.
        **kwargs: Additional keyword arguments representing HTTP headers.
        
        Summary:
        This method initializes an instance of the HTTPHeaderDict class by accepting either a dictionary-like object or keyword arguments as input. It supports copying from another HTTPHeaderDict instance or extending with a dictionary. The headers are then added to the instance using the `extend` method.
        
        Attributes
        """

        dict.__init__(self)
        if headers is not None:
            if isinstance(headers, HTTPHeaderDict):
                self._copy_from(headers)
            else:
                self.extend(headers)
        if kwargs:
            self.extend(kwargs)

    def __setitem__(self, key, val):
        return _dict_setitem(self, key.lower(), (key, val))

    def __getitem__(self, key):
        val = _dict_getitem(self, key.lower())
        return ', '.join(val[1:])

    def __delitem__(self, key):
        return _dict_delitem(self, key.lower())

    def __contains__(self, key):
        return _dict_contains(self, key.lower())

    def __eq__(self, other):
        """
        Check if two mappings are equal.
        
        Args:
        other (Mapping or object with 'keys' attribute): The object to compare against.
        
        Returns:
        bool: True if the two mappings are equal, False otherwise.
        
        Notes:
        - If `other` is neither a Mapping nor has a 'keys' attribute, the function returns False.
        - If `other` is not of the same type as the current instance, it is converted to the same type using `type(self)(
        """

        if not isinstance(other, Mapping) and not hasattr(other, 'keys'):
            return False
        if not isinstance(other, type(self)):
            other = type(self)(other)
        return dict((k1, self[k1]) for k1 in self) == dict((k2, other[k2]) for k2 in other)

    def __ne__(self, other):
        return not self.__eq__(other)

    values = MutableMapping.values
    get = MutableMapping.get
    update = MutableMapping.update
    
    if not PY3: # Python 2
        iterkeys = MutableMapping.iterkeys
        itervalues = MutableMapping.itervalues

    __marker = object()

    def pop(self, key, default=__marker):
        '''D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
          If key is not found, d is returned if given, otherwise KeyError is raised.
        '''
        # Using the MutableMapping function directly fails due to the private marker.
        # Using ordinary dict.pop would expose the internal structures.
        # So let's reinvent the wheel.
        try:
            value = self[key]
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            del self[key]
            return value

    def discard(self, key):
        """
        Discard the specified key from the dictionary.
        
        Args:
        key (Any): The key to be removed from the dictionary.
        
        Returns:
        None: This method does not return any value. It modifies the dictionary in place by removing the specified key if it exists.
        
        Raises:
        KeyError: If the specified key is not found in the dictionary.
        """

        try:
            del self[key]
        except KeyError:
            pass

    def add(self, key, val):
        """Adds a (name, value) pair, doesn't overwrite the value if it already
        exists.

        >>> headers = HTTPHeaderDict(foo='bar')
        >>> headers.add('Foo', 'baz')
        >>> headers['foo']
        'bar, baz'
        """
        key_lower = key.lower()
        new_vals = key, val
        # Keep the common case aka no item present as fast as possible
        vals = _dict_setdefault(self, key_lower, new_vals)
        if new_vals is not vals:
            # new_vals was not inserted, as there was a previous one
            if isinstance(vals, list):
                # If already several items got inserted, we have a list
                vals.append(val)
            else:
                # vals should be a tuple then, i.e. only one item so far
                # Need to convert the tuple to list for further extension
                _dict_setitem(self, key_lower, [vals[0], vals[1], val])

    def extend(self, *args, **kwargs):
        """Generic import function for any type of header-like object.
        Adapted version of MutableMapping.update in order to insert items
        with self.add instead of self.__setitem__
        """
        if len(args) > 1:
            raise TypeError("extend() takes at most 1 positional "
                            "arguments ({} given)".format(len(args)))
        other = args[0] if len(args) >= 1 else ()
        
        if isinstance(other, HTTPHeaderDict):
            for key, val in other.iteritems():
                self.add(key, val)
        elif isinstance(other, Mapping):
            for key in other:
                self.add(key, other[key])
        elif hasattr(other, "keys"):
            for key in other.keys():
                self.add(key, other[key])
        else:
            for key, value in other:
                self.add(key, value)

        for key, value in kwargs.items():
            self.add(key, value)

    def getlist(self, key):
        """Returns a list of all the values for the named field. Returns an
        empty list if the key doesn't exist."""
        try:
            vals = _dict_getitem(self, key.lower())
        except KeyError:
            return []
        else:
            if isinstance(vals, tuple):
                return [vals[1]]
            else:
                return vals[1:]

    # Backwards compatibility for httplib
    getheaders = getlist
    getallmatchingheaders = getlist
    iget = getlist

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, dict(self.itermerged()))

    def _copy_from(self, other):
        """
        Copies values from another dictionary or object into the current instance.
        
        Args:
        other (dict or object): The source dictionary or object to copy values from.
        
        This method iterates over the keys of the `other` dictionary or object. For each key, it retrieves the corresponding value using `_dict_getitem`. If the value is a list, it converts it to a Python list (if it's not already one). Then, it sets the value in the current instance using `_dict
        """

        for key in other:
            val = _dict_getitem(other, key)
            if isinstance(val, list):
                # Don't need to convert tuples
                val = list(val)
            _dict_setitem(self, key, val)

    def copy(self):
        """
        Copies the current object and returns a new instance.
        
        This method creates a new instance of the same class (`type(self)`),
        and then calls the `_copy_from` method to copy the attributes from
        the current object to the new instance. The new instance is then
        returned.
        
        Args:
        None
        
        Returns:
        A new instance of the same class as the current object, with
        copied attributes.
        
        Attributes:
        _copy_from: Method used to
        """

        clone = type(self)()
        clone._copy_from(self)
        return clone

    def iteritems(self):
        """Iterate over all header lines, including duplicate ones."""
        for key in self:
            vals = _dict_getitem(self, key)
            for val in vals[1:]:
                yield vals[0], val

    def itermerged(self):
        """Iterate over all headers, merging duplicate ones together."""
        for key in self:
            val = _dict_getitem(self, key)
            yield val[0], ', '.join(val[1:])

    def items(self):
        return list(self.iteritems())

    @classmethod
    def from_httplib(cls, message): # Python 2
        """Read headers from a Python 2 httplib message object."""
        # python2.7 does not expose a proper API for exporting multiheaders
        # efficiently. This function re-reads raw lines from the message 
        # object and extracts the multiheaders properly.
        headers = []
         
        for line in message.headers:
            if line.startswith((' ', '\t')):
                key, value = headers[-1]
                headers[-1] = (key, value + '\r\n' + line.rstrip())
                continue
    
            key, value = line.split(':', 1)
            headers.append((key, value.strip()))

        return cls(headers)
