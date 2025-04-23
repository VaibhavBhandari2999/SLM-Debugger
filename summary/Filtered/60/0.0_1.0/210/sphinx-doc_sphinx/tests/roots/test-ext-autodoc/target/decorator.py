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
        This is a decorator function that takes a function as input and returns a wrapper function. The wrapper function does not have any parameters or keywords and simply returns the result of the input function.
        
        Parameters:
        func (function): The function to be decorated.
        
        Returns:
        function: The wrapper function that calls the input function and returns its result.
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
