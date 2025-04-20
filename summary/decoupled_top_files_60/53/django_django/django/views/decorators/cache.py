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
        page_timeout=timeout, cache_alias=cache, key_prefix=key_prefix,
    )


def cache_control(**kwargs):
    def _cache_controller(viewfunc):
        """
        Function to cache a view function.
        
        This function is a decorator that wraps a view function and adds caching control to the HTTP response. It modifies the response by applying the specified cache control settings.
        
        Parameters:
        viewfunc (function): The view function to be wrapped and cached.
        kwargs (dict): A dictionary containing cache control settings such as 'max_age', 'public', 'private', 'must_revalidate', etc.
        
        Returns:
        function: A wrapped view function that applies cache control settings to
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
        _wrapped_view_func is a function that wraps around a view function to add never cache headers to the response. It takes a request object, any number of positional arguments, and any number of keyword arguments. The function returns a response object.
        
        Parameters:
        - request: HttpRequest object representing the incoming HTTP request.
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        
        Returns:
        - response: HttpResponse object with never cache headers added.
        
        Key Functions:
        - view_func: The view
        """

        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
w_func
