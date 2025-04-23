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
        Function decorator that modifies the response object by patching the vary headers based on the provided headers list.
        
        Parameters:
        func (callable): The function to be decorated.
        headers (list): A list of header names to be added to the 'Vary' header of the response.
        
        Returns:
        callable: A wrapped function that applies the specified headers to the response's 'Vary' header before returning it.
        
        Usage:
        @patch_vary_headers_decorator(['Cookie', 'Authorization'])
        def
        """

        response = func(*args, **kwargs)
        patch_vary_headers(response, ('Cookie',))
        return response
    return inner_func
