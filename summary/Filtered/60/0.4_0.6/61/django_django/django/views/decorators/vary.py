from functools import wraps

from django.utils.cache import patch_vary_headers


def vary_on_headers(*headers):
    """
    A view decorator that adds the specified headers to the Vary header of the
    response. Usage:

       @vary_on_headers('Cookie', 'Accept-language')
       def index(request):
           ...

    Note that the header names are not case-sensitive.
    """
    def decorator(func):
        """
        This function is a decorator that wraps another function (func) to modify its behavior. It takes a single argument, func, which is the function to be decorated. The decorator adds headers to the response object (response) using the patch_vary_headers method. The headers to be added are specified in the 'headers' parameter. The decorator returns the modified response object.
        
        Parameters:
        - func (function): The function to be decorated.
        
        Returns:
        - function: The decorated function that modifies the response with
        """

        @wraps(func)
        def inner_func(*args, **kwargs):
            response = func(*args, **kwargs)
            patch_vary_headers(response, headers)
            return response
        return inner_func
    return decorator


def vary_on_cookie(func):
    """
    A view decorator that adds "Cookie" to the Vary header of a response. This
    indicates that a page's contents depends on cookies. Usage:

        @vary_on_cookie
        def index(request):
            ...
    """
    @wraps(func)
    def inner_func(*args, **kwargs):
        """
        Function to modify the response object by patching vary headers with 'Cookie'.
        
        Parameters:
        func (callable): The function to be wrapped, expected to return a response object.
        *args: Variable length argument list to be passed to the wrapped function.
        **kwargs: Arbitrary keyword arguments to be passed to the wrapped function.
        
        Returns:
        response (HTTPResponse): The modified response object with vary headers patched.
        
        This function is designed to be used as a decorator to wrap other functions that return an
        """

        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
