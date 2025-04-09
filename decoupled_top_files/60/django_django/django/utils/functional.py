"""
This Python file contains utility functions and classes designed to work with lazy evaluations and proxies. The key components are:

1. **cached_property**: A decorator that converts a method into a cached property on an instance.
2. **classproperty**: A decorator that turns a method into a class-level property.
3. **Promise**: A base class for proxy classes created in the closure of lazy functions.
4. **lazy**: A decorator that turns any callable into a lazy-evaluated callable, with support for result classes.
5. **keep_lazy**: A decorator that allows a function to be called with one or more lazy arguments, evaluating them when necessary.
6. **keep_lazy_text**: A specialized version of `keep_lazy` for functions returning text
"""
import copy
import itertools
import operator
from functools import total_ordering, wraps


class cached_property:
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    A cached property can be made out of an existing method:
    (e.g. ``url = cached_property(get_absolute_url)``).
    The optional ``name`` argument is obsolete as of Python 3.6 and will be
    deprecated in Django 4.0 (#30127).
    """
    name = None

    @staticmethod
    def func(instance):
        """
        Raises a TypeError if the `func` is not called with an `instance` argument. The function checks if the `instance` argument is provided, and if not, raises a TypeError with a specific message indicating that the `__set_name__()` method must be called on the cached_property instance before using it.
        
        Args:
        instance (object): The instance of the class where the property is being defined.
        
        Raises:
        TypeError: If the `instance` argument is not provided.
        """

        raise TypeError(
            'Cannot use cached_property instance without calling '
            '__set_name__() on it.'
        )

    def __init__(self, func, name=None):
        self.real_func = func
        self.__doc__ = getattr(func, '__doc__')

    def __set_name__(self, owner, name):
        """
        Set the name of the cached property.
        
        Args:
        owner (type): The class that owns the property.
        name (str): The name of the property.
        
        Raises:
        TypeError: If the same cached property is assigned to two different names.
        
        This method sets the name of the cached property and ensures that the same property is not assigned to multiple names.
        """

        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                "(%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        """
        Call the function and put the return value in instance.__dict__ so that
        subsequent attribute access on the instance returns the cached value
        instead of calling cached_property.__get__().
        """
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class Promise:
    """
    Base class for the proxy class created in the closure of the lazy function.
    It's used to recognize promises in code.
    """
    pass


def lazy(func, *resultclasses):
    """
    Turn any callable into a lazy evaluated callable. result classes or types
    is required -- at least one is needed so that the automatic forcing of
    the lazy evaluation code is triggered. Results are not memoized; the
    function is evaluated on every access.
    """

    @total_ordering
    class __proxy__(Promise):
        """
        Encapsulate a function call and act as a proxy for methods that are
        called on the result of that function. The function is not evaluated
        until one of the methods on the result is called.
        """
        __prepared = False

        def __init__(self, args, kw):
            """
            Initialize a new instance of the class.
            
            Args:
            args (tuple): Positional arguments passed to the class constructor.
            kw (dict): Keyword arguments passed to the class constructor.
            
            Returns:
            None
            
            Effects:
            - Stores the positional arguments in `self.__args`.
            - Stores the keyword arguments in `self.__kw`.
            - If the class has not been prepared, calls `__prepare_class__()` to prepare it.
            - Sets `__class__.__prepared
            """

            self.__args = args
            self.__kw = kw
            if not self.__prepared:
                self.__prepare_class__()
            self.__class__.__prepared = True

        def __reduce__(self):
            """
            __reduce__(self) -> tuple
            
            This method is used to support pickle serialization. It returns a tuple that can be used to reconstruct an object of this class. The returned tuple contains the following elements:
            
            - `_lazy_proxy_unpickle`: A function used to unpickle the object.
            - `func`: The function to be proxied.
            - `self.__args`: The positional arguments to be passed to the function.
            - `self.__kw`: The keyword arguments to be
            """

            return (
                _lazy_proxy_unpickle,
                (func, self.__args, self.__kw) + resultclasses
            )

        def __repr__(self):
            return repr(self.__cast())

        @classmethod
        def __prepare_class__(cls):
            """
            Prepares a class by adding methods from specified result classes. This function iterates through each result class, then through its method resolution order (MRO) to find methods that are not already defined in the class. It uses a special method `__promise__` to create these methods dynamically. The function also sets flags `_delegate_bytes` and `_delegate_text` based on whether any of the result classes are `bytes` or `str`. If either flag is set, it overrides the `
            """

            for resultclass in resultclasses:
                for type_ in resultclass.mro():
                    for method_name in type_.__dict__:
                        # All __promise__ return the same wrapper method, they
                        # look up the correct implementation when called.
                        if hasattr(cls, method_name):
                            continue
                        meth = cls.__promise__(method_name)
                        setattr(cls, method_name, meth)
            cls._delegate_bytes = bytes in resultclasses
            cls._delegate_text = str in resultclasses
            assert not (cls._delegate_bytes and cls._delegate_text), (
                "Cannot call lazy() with both bytes and text return types.")
            if cls._delegate_text:
                cls.__str__ = cls.__text_cast
            elif cls._delegate_bytes:
                cls.__bytes__ = cls.__bytes_cast

        @classmethod
        def __promise__(cls, method_name):
            """
            Generates a wrapper function for a specified method.
            
            This function creates a wrapper that automatically evaluates a lazy value
            and applies the given magic method of the result type.
            
            Args:
            cls (type): The class to which the wrapper will be applied.
            method_name (str): The name of the magic method to be applied to the result.
            
            Returns:
            function: A wrapped function that evaluates the lazy value and applies the specified magic method.
            """

            # Builds a wrapper around some magic method
            def __wrapper__(self, *args, **kw):
                """
                __wrapper__: A wrapper function that automatically triggers the evaluation of a lazy value and applies the given magic method of the result type.
                
                Args:
                self: The instance of the class containing the wrapper.
                *args: Variable length argument list passed to the magic method.
                **kw: Arbitrary keyword arguments passed to the magic method.
                
                Returns:
                The result of applying the specified magic method to the evaluated lazy value.
                
                Summary:
                This function is a wrapper that takes a lazy value
                """

                # Automatically triggers the evaluation of a lazy value and
                # applies the given magic method of the result type.
                res = func(*self.__args, **self.__kw)
                return getattr(res, method_name)(*args, **kw)
            return __wrapper__

        def __text_cast(self):
            return func(*self.__args, **self.__kw)

        def __bytes_cast(self):
            return bytes(func(*self.__args, **self.__kw))

        def __bytes_cast_encoded(self):
            return func(*self.__args, **self.__kw).encode()

        def __cast(self):
            """
            Casts the input data based on the delegate type.
            
            Args:
            None (The function uses instance variables to determine the type of cast).
            
            Returns:
            The casted data based on the delegate type.
            
            Raises:
            None (The function does not explicitly handle any exceptions).
            
            Notes:
            - If `_delegate_bytes` is True, the function calls `__bytes_cast()`.
            - If `_delegate_text` is True, the function calls `__text_cast()`.
            """

            if self._delegate_bytes:
                return self.__bytes_cast()
            elif self._delegate_text:
                return self.__text_cast()
            else:
                return func(*self.__args, **self.__kw)

        def __str__(self):
            """
            Return a string representation of the object after casting it using the `__cast__` method.
            
            This method is overridden to ensure that the string representation of the object is generated based on its casted form, rather than its original form. The `__cast__()` method is called to transform the object before generating the string representation.
            
            Returns:
            str: A string representation of the object after casting.
            """

            # object defines __str__(), so __prepare_class__() won't overload
            # a __str__() method from the proxied class.
            return str(self.__cast())

        def __eq__(self, other):
            """
            Compares the current promise with another object for equality.
            
            Args:
            other (Promise): The other promise to compare against.
            
            Returns:
            bool: True if the two promises are equal after casting, False otherwise.
            
            Notes:
            - If `other` is an instance of `Promise`, it is casted using `other.__cast()`.
            - The current promise is casted using `self.__cast()` before comparison.
            """

            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() == other

        def __lt__(self, other):
            """
            Compares this promise with another object for less-than ordering.
            
            Args:
            other (Promise): The other promise to compare against.
            
            Returns:
            bool: True if this promise is less than the other promise, False otherwise.
            
            Notes:
            - If `other` is an instance of `Promise`, it is casted using the `__cast()` method.
            - Both promises are casted using the `__cast()` method before comparison.
            - The comparison is performed using the
            """

            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() < other

        def __hash__(self):
            return hash(self.__cast())

        def __mod__(self, rhs):
            """
            Modulo operator for custom string formatting.
            
            This method performs modulo operation on the current instance with the provided right-hand side (rhs) value. If the instance has a delegate text, it converts the instance to a string using `str()` and applies the modulo operation using the `%` operator. Otherwise, it casts the instance to a numeric type using `__cast()` and then performs the modulo operation.
            
            Args:
            rhs (object): The right-hand side value to perform modulo operation with.
            """

            if self._delegate_text:
                return str(self) % rhs
            return self.__cast() % rhs

        def __deepcopy__(self, memo):
            """
            Deep copies an instance of the class. Since instances of this class are effectively immutable and consist only of functions, no complex copying is required. The function uses the `memo` dictionary to prevent infinite recursion when dealing with circular references. The original instance is returned.
            
            Args:
            self: The instance of the class to be copied.
            memo (dict): A dictionary used to track objects that have already been copied to avoid infinite recursion.
            
            Returns:
            The original instance of the class.
            """

            # Instances of this class are effectively immutable. It's just a
            # collection of functions. So we don't need to do anything
            # complicated for copying.
            memo[id(self)] = self
            return self

    @wraps(func)
    def __wrapper__(*args, **kw):
        # Creates the proxy object, instead of the actual value.
        return __proxy__(args, kw)

    return __wrapper__


def _lazy_proxy_unpickle(func, args, kwargs, *resultclasses):
    return lazy(func, *resultclasses)(*args, **kwargs)


def lazystr(text):
    """
    Shortcut for the common case of a lazy callable that returns str.
    """
    return lazy(str, str)(text)


def keep_lazy(*resultclasses):
    """
    A decorator that allows a function to be called with one or more lazy
    arguments. If none of the args are lazy, the function is evaluated
    immediately, otherwise a __proxy__ is returned that will evaluate the
    function when needed.
    """
    if not resultclasses:
        raise TypeError("You must pass at least one argument to keep_lazy().")

    def decorator(func):
        """
        This decorator function `decorator` takes a function `func` as an argument and returns a wrapped function `wrapper`. The wrapped function checks if any of the arguments passed to it are instances of `Promise`, a class that represents a deferred or lazy evaluation. If so, it calls the `lazy_func` function with the same arguments, which is a lazy version of the original function `func`. Otherwise, it simply calls the original function `func` with the given arguments.
        
        Args:
        """

        lazy_func = lazy(func, *resultclasses)

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            wrapper(*args, **kwargs)
            This function acts as a wrapper around another function, `func`, and a lazy function, `lazy_func`. It checks if any of the arguments passed to it are instances of `Promise` using a generator expression with `itertools.chain` to iterate over both positional (`args`) and keyword (`kwargs`) arguments. If any argument is a `Promise`, it calls the `lazy_func` with the same arguments; otherwise, it calls the original `func`
            """

            if any(isinstance(arg, Promise) for arg in itertools.chain(args, kwargs.values())):
                return lazy_func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def keep_lazy_text(func):
    """
    A decorator for functions that accept lazy arguments and return text.
    """
    return keep_lazy(str)(func)


empty = object()


def new_method_proxy(func):
    """
    This function acts as a proxy for the original method. It checks if the '_wrapped' attribute of the instance is 'empty'. If it is, it calls the '_setup()' method. Then, it calls the original method 'func' with the '_wrapped' attribute and any additional arguments passed to the function. The function returns the result of the original method call.
    
    Args:
    self (object): The instance of the class that the method is being called on.
    *args: Additional
    """

    def inner(self, *args):
        """
        inner(self, *args) -> Any
        
        This method is responsible for initializing the wrapped object if it is not already initialized, and then calling the specified function `func` with the wrapped object and any additional arguments passed to this method.
        
        Parameters:
        - self: The instance of the class containing the `_wrapped` attribute and the `_setup` method.
        - *args: Variable length argument list to be passed to the function `func`.
        
        Returns:
        - Any: The result
        """

        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazyObject:
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.

    By subclassing, you have the opportunity to intercept and alter the
    instantiation. If you don't need to do that, use SimpleLazyObject.
    """

    # Avoid infinite recursion when tracing __init__ (#19456).
    _wrapped = None

    def __init__(self):
        """
        Initialize the object with an empty wrapped value.
        """

        # Note: if a subclass overrides __init__(), it will likely need to
        # override __copy__() and __deepcopy__() as well.
        self._wrapped = empty

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self, name, value):
        """
        Sets an attribute on the instance.
        
        Args:
        name (str): The name of the attribute to set.
        value: The value to assign to the attribute.
        
        Notes:
        - If the attribute name is '_wrapped', it is directly assigned to the instance's dictionary to avoid infinite recursion.
        - If the attribute name is not '_wrapped' and the wrapped object is not yet initialized (i.e., `_wrapped` is `empty`), the wrapped object is initialized by calling `_
        """

        if name == "_wrapped":
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        """
        Delete an attribute from the object.
        
        Args:
        name (str): The name of the attribute to be deleted.
        
        Raises:
        TypeError: If the attribute to be deleted is '_wrapped'.
        AttributeError: If the attribute does not exist in the wrapped object.
        
        Notes:
        - This method first checks if the attribute to be deleted is '_wrapped'. If so, it raises a TypeError.
        - If the wrapped object is empty, it calls the `_setup` method to initialize it
        """

        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        Must be implemented by subclasses to initialize the wrapped object.
        """
        raise NotImplementedError('subclasses of LazyObject must provide a _setup() method')

    # Because we have messed with __class__ below, we confuse pickle as to what
    # class we are pickling. We're going to have to initialize the wrapped
    # object to successfully pickle it, so we might as well just pickle the
    # wrapped object since they're supposed to act the same way.
    #
    # Unfortunately, if we try to simply act like the wrapped object, the ruse
    # will break down when pickle gets our id(). Thus we end up with pickle
    # thinking, in effect, that we are a distinct object from the wrapped
    # object, but with the same __dict__. This can cause problems (see #25389).
    #
    # So instead, we define our own __reduce__ method and custom unpickler. We
    # pickle the wrapped object as the unpickler's argument, so that pickle
    # will pickle it normally, and then the unpickler simply returns its
    # argument.
    def __reduce__(self):
        """
        Reduces the LazyObject instance to a tuple that can be used for pickling. If the wrapped object is empty, it initializes the wrapped object. Returns a tuple containing the unpickle_lazyobject function and the wrapped object.
        """

        if self._wrapped is empty:
            self._setup()
        return (unpickle_lazyobject, (self._wrapped,))

    def __copy__(self):
        """
        Copy the current object.
        
        If the object is uninitialized (i.e., `_wrapped` is `empty`), create a new
        instance of the same type (`type(self)`). Otherwise, return a shallow copy
        of the wrapped object using `copy.copy()`.
        
        Args:
        None
        
        Returns:
        A new instance of the same type as the current object or a shallow copy
        of the wrapped object.
        """

        if self._wrapped is empty:
            # If uninitialized, copy the wrapper. Use type(self), not
            # self.__class__, because the latter is proxied.
            return type(self)()
        else:
            # If initialized, return a copy of the wrapped object.
            return copy.copy(self._wrapped)

    def __deepcopy__(self, memo):
        """
        Deep copies the given object using the specified memo dictionary. If the wrapped object is empty, creates an instance of the same class and returns it. Otherwise, uses `copy.deepcopy` to perform a deep copy of the wrapped object.
        
        Args:
        self: The object to be copied.
        memo (dict): A dictionary used to track objects already copied.
        
        Returns:
        The deep copy of the object or the wrapped object if it's not empty.
        """

        if self._wrapped is empty:
            # We have to use type(self), not self.__class__, because the
            # latter is proxied.
            result = type(self)()
            memo[id(self)] = result
            return result
        return copy.deepcopy(self._wrapped, memo)

    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)

    # Introspection support
    __dir__ = new_method_proxy(dir)

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __gt__ = new_method_proxy(operator.gt)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)

    # List/Tuple/Dictionary methods support
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


def unpickle_lazyobject(wrapped):
    """
    Used to unpickle lazy objects. Just return its argument, which will be the
    wrapped object.
    """
    return wrapped


class SimpleLazyObject(LazyObject):
    """
    A lazy object initialized from any function.

    Designed for compound objects of unknown type. For builtins or objects of
    known type, use django.utils.functional.lazy.
    """
    def __init__(self, func):
        """
        Pass in a callable that returns the object to be wrapped.

        If copies are made of the resulting SimpleLazyObject, which can happen
        in various circumstances within Django, then you must ensure that the
        callable can be safely run more than once and will return the same
        value.
        """
        self.__dict__['_setupfunc'] = func
        super().__init__()

    def _setup(self):
        self._wrapped = self._setupfunc()

    # Return a meaningful representation of the lazy object for debugging
    # without evaluating the wrapped object.
    def __repr__(self):
        """
        Return a string representation of the object.
        
        If the wrapped object is empty, the `__repr__` method of the `_setupfunc`
        attribute is called. Otherwise, the `__repr__` method of the `_wrapped`
        attribute is called. The result is formatted as a string with the class
        name and the value of the relevant attribute.
        
        Args:
        None
        
        Returns:
        str: A string representation of the object.
        
        Raises:
        None
        """

        if self._wrapped is empty:
            repr_attr = self._setupfunc
        else:
            repr_attr = self._wrapped
        return '<%s: %r>' % (type(self).__name__, repr_attr)

    def __copy__(self):
        """
        Copy the current instance.
        
        If the instance is uninitialized (i.e., `_wrapped` is `empty`), create a new
        `SimpleLazyObject` with the same setup function (`_setupfunc`). Otherwise,
        return a shallow copy of the wrapped object (`_wrapped`).
        
        Args:
        None
        
        Returns:
        A new instance of `SimpleLazyObject` or a shallow copy of the wrapped
        object, depending on the initialization state of the current instance.
        """

        if self._wrapped is empty:
            # If uninitialized, copy the wrapper. Use SimpleLazyObject, not
            # self.__class__, because the latter is proxied.
            return SimpleLazyObject(self._setupfunc)
        else:
            # If initialized, return a copy of the wrapped object.
            return copy.copy(self._wrapped)

    def __deepcopy__(self, memo):
        """
        Deep copies the current object or its wrapped content.
        
        This method handles the deep copying of an object, either by directly
        copying the wrapped content using `copy.deepcopy` or by creating a new
        `SimpleLazyObject` instance if the wrapped content is empty.
        
        Args:
        memo (dict): A dictionary used to keep track of already copied objects
        to avoid infinite recursion.
        
        Returns:
        The deep-copied version of the current object or its wrapped content.
        """

        if self._wrapped is empty:
            # We have to use SimpleLazyObject, not self.__class__, because the
            # latter is proxied.
            result = SimpleLazyObject(self._setupfunc)
            memo[id(self)] = result
            return result
        return copy.deepcopy(self._wrapped, memo)


def partition(predicate, values):
    """
    Split the values into two sets, based on the return value of the function
    (True/False). e.g.:

        >>> partition(lambda x: x > 3, range(5))
        [0, 1, 2, 3], [4]
    """
    results = ([], [])
    for item in values:
        results[predicate(item)].append(item)
    return results
