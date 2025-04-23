from functools import wraps


def deco1(func):
    """docstring for deco1"""
    @wraps(func)
    def wrapper():
        return func()

    return wrapper


def deco2(condition, message):
    """docstring for deco2"""
    def decorator(func):
        """
        This function is a decorator that wraps another function, `func`. It does not take any parameters or keyword arguments. When `func` is called within the wrapper, it returns the result of `func()`. The decorator does not modify the behavior of `func` but simply encapsulates it.
        
        Parameters:
        None
        
        Returns:
        The return value of the function `func` when it is called.
        
        Usage:
        @decorator
        def some_function():
        # Function implementation
        
        some
        """

        def wrapper():
            return func()

        return wrapper
    return decorator


@deco1
def foo(name=None, age=None):
    pass


class Bar:
    @deco1
    def meth(self, name=None, age=None):
        pass


class Baz:
    @deco1
    def __init__(self, name=None, age=None):
        pass


class Qux:
    @deco1
    def __new__(self, name=None, age=None):
        pass


class _Metaclass(type):
    @deco1
    def __call__(self, name=None, age=None):
        pass


class Quux(metaclass=_Metaclass):
    pass
