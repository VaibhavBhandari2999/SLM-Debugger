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
        This function is a decorator that wraps another function (func) and modifies its response. It accepts any number of positional arguments (*args) and keyword arguments (**kwargs). The wrapped function is expected to return a response object. After calling the original function, the `patch_vary_headers` function is called with the response object and a list of headers (headers). This function updates the 'Vary' header of the response to ensure that the response is properly cached. The output of this function is the
        """

        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
