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
        page_timeout=timeout,
        cache_alias=cache,
        key_prefix=key_prefix,
    )


def cache_control(**kwargs):
    """
    Decorator to add cache control headers to a view function. The decorator accepts keyword arguments that are passed to the patch_cache_control function to set various cache-related HTTP headers. The decorated view function must return a response object.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments representing cache control directives.
    
    Returns:
    A wrapped view function that adds cache control headers to the response.
    
    Usage:
    @cache_control(max_age=3600, public=True)
    def my_view(request):
    # Your view
    """

    def _cache_controller(viewfunc):
        """
        Decorator to control caching behavior of a view function.
        
        This function wraps a view function to apply caching settings to the HTTP response. It ensures that the wrapped function receives an HttpRequest object and modifies the response with the specified cache control settings.
        
        Parameters:
        viewfunc (function): The view function to be decorated.
        
        Returns:
        function: A wrapped function that applies cache control settings to the HTTP response.
        
        Raises:
        TypeError: If the view function does not receive an HttpRequest object as its first argument.
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            Cache-Control Decorator for HTTP Responses
            
            This function is designed to be used as a decorator for HTTP views. It ensures that the view function returns a response object and then applies cache control settings to that response.
            
            Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments, used to set cache control directives.
            
            Returns:
            HttpResponse: The modified HTTP response object with cache control settings applied.
            
            Raises:
            TypeError: If
            """

            # Ensure argument looks like a request.
            if not hasattr(request, "META"):
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
    def _wrapper_view_func(request, *args, **kwargs):
        # Ensure argument looks like a request.
        if not hasattr(request, "META"):
            raise TypeError(
                "never_cache didn't receive an HttpRequest. If you are "
                "decorating a classmethod, be sure to use @method_decorator."
            )
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response

    return _wrapper_view_func
