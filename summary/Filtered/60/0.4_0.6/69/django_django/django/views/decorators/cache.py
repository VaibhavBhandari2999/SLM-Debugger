from functools import wraps

from django.http import HttpRequest
from django.middleware.cache import CacheMiddleware
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.utils.decorators import decorator_from_middleware_with_args


def cache_page(timeout, *, cache=None, key_prefix=None):
    """
    Decorator for views that tries getting the page from the cache and
    populates the cache if the page isn't in the cache yet.

    The cache is keyed by the URL and some data from the headers.
    Additionally there is the key prefix that is used to distinguish different
    cache areas in a multi-site setup. You could use the
    get_current_site().domain, for example, as that is unique across a Django
    project.

    Additionally, all headers from the response's Vary header will be taken
    into account on caching -- just like the middleware does.
    """
    return decorator_from_middleware_with_args(CacheMiddleware)(
        page_timeout=timeout, cache_alias=cache, key_prefix=key_prefix,
    )


def cache_control(**kwargs):
    """
    Decorator to control caching behavior of a view function.
    
    This function is a decorator that can be applied to Django view functions to
    modify the caching behavior of the response. It takes keyword arguments that
    are passed to the `patch_cache_control` function to set various cache-related
    headers.
    
    Parameters:
    **kwargs: Keyword arguments that specify the caching behavior. These
    arguments are passed to the `patch_cache_control` function.
    
    Returns:
    A decorated view function that sets the specified cache control headers
    """

    def _cache_controller(viewfunc):
        """
        Decorator to control caching behavior of a view function.
        
        This decorator wraps a view function to modify the HTTP response's cache control settings. It ensures that the view function receives an HttpRequest object and then applies the specified cache control settings to the response.
        
        Parameters:
        viewfunc (function): The view function to be decorated.
        
        Returns:
        function: A wrapped view function that applies cache control settings to the response.
        
        Raises:
        TypeError: If the input is not an HttpRequest object.
        
        Usage:
        @cache
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            if not isinstance(request, HttpRequest):
                raise TypeError(
                    "cache_control didn't receive an HttpRequest. If you are "
                    "decorating a classmethod, be sure to use "
                    "@method_decorator."
                )
            response = viewfunc(request, *args, **kw)
            patch_cache_control(response, **kwargs)
            return response
        return _cache_controlled
    return _cache_controller


def never_cache(view_func):
    """
    Decorator that adds headers to a response so that it will never be cached.
    """
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        """
        _wrapped_view_func is a function that wraps a view function to add never-cache headers to the response. It takes an HttpRequest object as the first argument and any number of positional and keyword arguments. If the first argument is not an instance of HttpRequest, it raises a TypeError. The function then calls the view function with the provided arguments, adds never-cache headers to the response, and returns the response.
        
        Parameters:
        - request (HttpRequest): The HTTP request object.
        - *args: Variable length argument list
        """

        if not isinstance(request, HttpRequest):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
