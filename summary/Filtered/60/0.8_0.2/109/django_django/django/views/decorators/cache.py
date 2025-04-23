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
    Decorator to control caching behavior of a view function. The decorated function should return an HttpResponse.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments that will be passed to the patch_cache_control function to modify the response's Cache-Control header.
    
    Returns:
    A wrapped view function that applies the specified cache control directives to the response.
    
    Usage:
    @cache_control(max_age=3600, public=True)
    def my_view(request):
    # Your view logic here
    return HttpResponse("Hello,
    """

    def _cache_controller(viewfunc):
        """
        Decorator to control caching behavior for a view function.
        
        This decorator wraps a view function and modifies the response with cache control headers. It ensures that the input is an HttpRequest and adds the specified cache control settings to the response.
        
        Parameters:
        viewfunc (function): The view function to be decorated.
        
        Returns:
        function: A wrapped function that applies cache control settings to the response.
        
        Raises:
        TypeError: If the input is not an HttpRequest.
        """

        @wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            """
            Function to apply cache control to a view function in Django.
            
            This function ensures that the input is an HttpRequest object, applies cache control settings to the response, and returns the response.
            
            Parameters:
            request (HttpRequest): The HTTP request object.
            viewfunc (function): The view function to be decorated.
            **kwargs: Keyword arguments to customize cache control settings.
            
            Returns:
            HttpResponse: The response from the view function with cache control settings applied.
            
            Raises:
            TypeError: If the input is not
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
