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
        A decorator function that wraps another function and returns a new function. The wrapped function does not take any parameters and does not return any value.
        
        Parameters:
        func (function): The function to be wrapped.
        
        Returns:
        function: A new function that does not take any parameters and does not return any value.
        
        Usage:
        @decorator
        def my_function():
        pass
        
        my_function()  # This will call the wrapper function, which in turn calls the original function.
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
