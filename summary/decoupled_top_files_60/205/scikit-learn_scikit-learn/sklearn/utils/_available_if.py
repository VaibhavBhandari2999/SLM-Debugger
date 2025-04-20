from types import MethodType
from functools import wraps
from functools import update_wrapper


class _AvailableIfDescriptor:
    """Implements a conditional property using the descriptor protocol.

    Using this class to create a decorator will raise an ``AttributeError``
    if check(self) returns a falsey value. Note that if check raises an error
    this will also result in hasattr returning false.

    See https://docs.python.org/3/howto/descriptor.html for an explanation of
    descriptors.
    """

    def __init__(self, fn, check, attribute_name):
        """
        A descriptor that enforces a specific condition on the value of an attribute.
        
        This descriptor is used to ensure that the value of the attribute `attribute_name` meets a certain condition defined by the `check` function. The `fn` function is the original function that this descriptor wraps.
        
        Parameters:
        fn (function): The original function that this descriptor wraps.
        check (function): A function that takes a single argument and returns True if the condition is met, False otherwise.
        attribute_name (
        """

        self.fn = fn
        self.check = check
        self.attribute_name = attribute_name

        # update the docstring of the descriptor
        update_wrapper(self, fn)

    def __get__(self, obj, owner=None):
        attr_err = AttributeError(
            f"This {repr(owner.__name__)} has no attribute {repr(self.attribute_name)}"
        )
        if obj is not None:
            # delegate only on instances, not the classes.
            # this is to allow access to the docstrings.
            if not self.check(obj):
                raise attr_err
            out = MethodType(self.fn, obj)

        else:
            # This makes it possible to use the decorated method as an unbound method,
            # for instance when monkeypatching.
            @wraps(self.fn)
            def out(*args, **kwargs):
                """
                Function to execute a wrapped function with input validation.
                
                Parameters:
                *args: Variable length argument list. The first argument is expected to be validated by the `check` method.
                **kwargs: Arbitrary keyword arguments passed to the wrapped function.
                
                Returns:
                The result of the wrapped function.
                
                Raises:
                attr_err: If the first argument in *args does not pass the validation check.
                
                This function is designed to wrap another function, ensuring that its input arguments meet certain criteria before executing it.
                """

                if not self.check(args[0]):
                    raise attr_err
                return self.fn(*args, **kwargs)

        return out


def available_if(check):
    """An attribute that is available only if check returns a truthy value.

    Parameters
    ----------
    check : callable
        When passed the object with the decorated method, this should return
        a truthy value if the attribute is available, and either return False
        or raise an AttributeError if not available.

    Returns
    -------
    callable
        Callable makes the decorated method available if `check` returns
        a truthy value, otherwise the decorated method is unavailable.

    Examples
    --------
    >>> from sklearn.utils.metaestimators import available_if
    >>> class HelloIfEven:
    ...    def __init__(self, x):
    ...        self.x = x
    ...
    ...    def _x_is_even(self):
    ...        return self.x % 2 == 0
    ...
    ...    @available_if(_x_is_even)
    ...    def say_hello(self):
    ...        print("Hello")
    ...
    >>> obj = HelloIfEven(1)
    >>> hasattr(obj, "say_hello")
    False
    >>> obj.x = 2
    >>> hasattr(obj, "say_hello")
    True
    >>> obj.say_hello()
    Hello
    """
    return lambda fn: _AvailableIfDescriptor(fn, check, attribute_name=fn.__name__)
