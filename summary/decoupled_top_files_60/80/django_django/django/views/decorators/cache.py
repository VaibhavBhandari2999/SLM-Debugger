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
    
    This function takes keyword arguments to customize the caching behavior of the decorated view function. It returns a new function that wraps the original view function, applying the specified cache control settings to the response.
    
    Parameters:
    **kwargs: Keyword arguments to customize the cache control settings. These will be passed to the patch_cache_control function to modify the response's cache control headers.
    
    Returns:
    A wrapped function that, when called, will apply the specified cache control
    """

    def _cache_controller(viewfunc):
        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            Cache-Control Decorator for Django Views
            
            This function is designed to be used as a decorator for Django views to control caching behavior. It ensures that the view function returns a response and then applies cache control settings to that response.
            
            Parameters:
            request (HttpRequest): The Django HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. These are used to set cache control directives such as max_age, public, etc.
            
            Returns:
            HttpResponse: The modified response
            """

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
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
