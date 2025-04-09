"""
This Python file contains decorators for controlling caching behavior in Django views. It defines three decorators:

1. `cache_page`: A decorator that caches the output of a view function based on the URL and additional headers. It leverages Django's built-in `CacheMiddleware`.

2. `cache_control`: A decorator that allows setting custom caching directives directly on the response using the `patch_cache_control` function. It can be used to specify various caching behaviors such as max-age, no-cache, etc.

3. `never_cache`: A decorator that ensures the response is never cached by adding appropriate headers to the response.

The decorators interact by modifying the response object to include caching-related headers. `cache_page` uses Django's `CacheMiddleware` to manage caching
"""
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
    Decorator that applies caching control to a view function. It takes keyword arguments to customize the caching behavior. The decorated view function receives an HttpRequest object as its first argument. The decorator modifies the response with the specified caching directives using the `patch_cache_control` function.
    
    Args:
    **kwargs: Keyword arguments specifying caching directives.
    
    Returns:
    A wrapped view function that applies caching control to the response.
    
    Raises:
    TypeError: If the request is not an instance of HttpRequest.
    """

    def _cache_controller(viewfunc):
        """
        Caches the response of a view function using the `patch_cache_control` function. This decorator ensures that the request is an instance of `HttpRequest`, and if not, raises a `TypeError`. The original view function is wrapped to modify the cache control headers of the response before returning it.
        
        Args:
        viewfunc (function): The view function to be cached.
        
        Returns:
        function: A wrapped version of the view function with cache control applied.
        
        Raises:
        TypeError: If the
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            Caches the response using cache_control and patch_cache_control functions. This function is designed to work with HttpRequest objects and modifies the response object by applying cache control settings.
            
            Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kw: Arbitrary keyword arguments.
            
            Returns:
            response: The modified HTTP response object with cache control settings applied.
            
            Raises:
            TypeError: If the input 'request' is not an instance of HttpRequest.
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
        """
        Decorator that adds never-cache headers to the response.
        
        This function takes an HttpRequest object as input and returns a response
        with never-cache headers added. It raises a TypeError if the input is not
        an instance of HttpRequest. The function uses the `add_never_cache_headers`
        function to modify the response headers.
        
        Args:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
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
