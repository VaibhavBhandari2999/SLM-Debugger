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
    Decorator to add cache control headers to a view function.
    
    This function returns a decorator that can be used to add cache control headers to a view function. The decorator takes keyword arguments that are passed to the `patch_cache_control` function to set the cache control headers.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments that are used to set the cache control headers.
    
    Returns:
    A decorator that can be applied to a view function to add cache control headers to the response.
    
    Example usage:
    @cache
    """

    def _cache_controller(viewfunc):
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
        _wrapped_view_func is a function that wraps a view function to add never-cache headers to the response. It first checks if the provided request is an instance of HttpRequest. If not, it raises a TypeError. Then, it calls the view function with the provided arguments and keyword arguments, and passes the resulting response to add_never_cache_headers to add the necessary headers. Finally, it returns the modified response.
        
        Parameters:
        - request (HttpRequest): The HTTP request object.
        - *args: Additional positional
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
