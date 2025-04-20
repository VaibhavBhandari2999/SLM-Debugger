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
        This function is a decorator that wraps another function. It takes a single argument, func, which is the function to be decorated. The decorator does not take any additional arguments and returns a new function, wrapper, which calls the original function and returns its result.
        
        Parameters:
        - func: The function to be decorated.
        
        Returns:
        - A new function, wrapper, which calls the original function and returns its result.
        
        Example usage:
        @decorator
        def example_function():
        return "Hello, world!"
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
