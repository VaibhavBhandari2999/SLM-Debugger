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
        Generate a response from a function and modify the response headers.
        
        This function takes a callable `func` and any number of positional (*args) and keyword (**kwargs) arguments. It calls `func` with these arguments, then modifies the response headers using the `patch_vary_headers` function with the specified `headers`. The function returns the modified response.
        
        Parameters:
        func (callable): The function to be called and whose response is to be modified.
        *args: Variable length argument list to
        """

        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
