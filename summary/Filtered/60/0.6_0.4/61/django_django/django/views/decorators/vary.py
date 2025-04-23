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
        This function is a decorator that wraps another function (func) and modifies its behavior. It takes a single argument, func, which is the function to be decorated. The decorator adds headers to the response object (response) using the patch_vary_headers method. The headers to be added are specified in the 'headers' parameter. The decorator returns the modified response object.
        
        Parameters:
        - func: The function to be decorated.
        
        Returns:
        - The modified response object with added headers.
        
        Key Parameters:
        -
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
        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
