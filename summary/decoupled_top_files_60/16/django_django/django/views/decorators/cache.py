from functools import wraps

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
        cache_timeout=timeout, cache_alias=cache, key_prefix=key_prefix
    )


def cache_control(**kwargs):
    def _cache_controller(viewfunc):
        """
        Decorator to control caching for a Django view function.
        
        This function wraps a Django view function to add caching headers to the HTTP response. The decorator takes a dictionary of cache control options as a keyword argument.
        
        Parameters:
        viewfunc (function): The Django view function to be wrapped.
        
        Returns:
        function: A wrapped view function with caching headers applied.
        
        Usage:
        @cache_controller({'max_age': 3600, 'public': True})
        def my_view(request):
        # View
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
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
        _wrapped_view_func is a function that wraps a view function to add never cache headers to the response.
        
        Parameters:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        HttpResponse: The HTTP response object with never cache headers added.
        
        This function is typically used to ensure that the response from a view function is not cached by the browser or any intermediary caches.
        """

        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
