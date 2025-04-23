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
    
    This function returns a decorator that can be applied to a view function to
    add cache control headers to the HTTP response. The headers are specified via
    keyword arguments.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments representing cache control directives
    such as 'max_age', 'public', 'private', 'no_cache', 'must_revalidate',
    'proxy_revalidate', and 's_maxage'.
    
    Returns:
    A decorator that can be
    """

    def _cache_controller(viewfunc):
        """
        Decorator to control caching behavior of a view function.
        
        This function wraps a view function to add caching headers to the HTTP response.
        It ensures that the input is an instance of HttpRequest and modifies the response
        with the specified caching directives.
        
        Parameters:
        viewfunc (function): The view function to be decorated.
        
        Returns:
        function: A wrapped function that adds caching headers to the HTTP response.
        
        Raises:
        TypeError: If the input is not an instance of HttpRequest.
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            Function to apply cache control to a view function in Django.
            
            This function is designed to be used as a decorator for view functions in Django. It ensures that the response from the view function is properly cached according to the specified cache control settings.
            
            Parameters:
            request (HttpRequest): The incoming HTTP request object.
            *args: Additional positional arguments to pass to the view function.
            **kwargs: Additional keyword arguments to pass to the view function.
            
            Returns:
            HttpResponse: The response from the view function
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
        Function to wrap a view function with never_cache functionality.
        
        This function ensures that the provided view function is never cached by adding appropriate headers to the HTTP response. It checks if the request is an instance of HttpRequest, and if not, raises a TypeError. The function then calls the view function with the provided arguments and keyword arguments, and adds never-cache headers to the response before returning it.
        
        Parameters:
        request (HttpRequest): The HTTP request object.
        *args: Additional positional arguments to pass to the
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
