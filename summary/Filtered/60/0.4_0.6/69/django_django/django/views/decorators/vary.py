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
        Function to modify the response object by patching vary headers with 'Cookie'. It accepts a function `func` as an argument, which is expected to return a response object. The function `inner_func` takes any number of positional arguments (*args) and keyword arguments (**kwargs) to pass through to `func`. The response object is then modified by adding 'Cookie' to the vary headers before returning it.
        
        Parameters:
        *args: Variable length argument list to be passed to the function `func
        """

        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
