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
        A decorator function that wraps another function. It takes a function `func` as input and returns a new function `wrapper` that does not accept any arguments. The `wrapper` function simply calls the original `func` and returns its result. This decorator can be used to modify the behavior of the decorated function without changing its implementation.
        
        Parameters:
        func (function): The function to be decorated.
        
        Returns:
        function: A new function that wraps the original function `func` and does not accept
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
