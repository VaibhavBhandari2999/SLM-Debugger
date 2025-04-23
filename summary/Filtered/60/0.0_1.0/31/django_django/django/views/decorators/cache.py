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
    """
    Generate a caching decorator for views.
    
    This function creates a caching decorator that can be applied to Django views. The decorator modifies the response's cache control settings based on the provided keyword arguments.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments that will be used to set the cache control headers. Common keys include 'max_age', 'public', 'private', 'must_revalidate', 'proxy_revalidate', 'no_transform', 'no_store', and 'no_cache'.
    
    Returns:
    A decorator that can
    """

    def _cache_controller(viewfunc):
        """
        Decorator to control caching for a view function.
        
        This function wraps a view function to apply caching controls to the HTTP response. The wrapped function will modify the response with the specified cache control settings.
        
        Parameters:
        viewfunc (function): The view function to be wrapped.
        
        Returns:
        function: A wrapped view function that applies cache control settings to the response.
        
        Usage:
        @cache_controller(max_age=3600, public=True)
        def my_view(request):
        # View logic here
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            _cache_controlled(request, *args, **kwargs)
            
            Cache-controlled view function.
            
            This function is designed to be used as a wrapper for view functions in web applications. It ensures that the response from the view function is properly cached according to the provided cache control settings.
            
            Parameters:
            request (HttpRequest): The incoming HTTP request object.
            *args: Variable length argument list to be passed to the view function.
            **kwargs: Arbitrary keyword arguments to be passed to the view function and the patch
            """

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
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
