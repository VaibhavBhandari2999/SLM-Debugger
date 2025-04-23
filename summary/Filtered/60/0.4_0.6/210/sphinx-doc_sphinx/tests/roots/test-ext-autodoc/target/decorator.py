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
        This function is a decorator that wraps another function and returns a new function. It does not take any parameters or keywords. The input is a function, and the output is a wrapped function.
        
        Parameters:
        func (function): The function to be wrapped.
        
        Returns:
        function: The wrapped function.
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
