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
    Generates a caching decorator for Django views.
    
    This function returns a decorator that can be applied to Django views to control caching behavior. The decorator sets the cache control headers on the response based on the provided keyword arguments.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments that will be used to set cache control directives on the response. Common directives include 'max_age', 'public', 'private', 'no_cache', 'must_revalidate', 'proxy_revalidate', and 's-maxage'.
    
    Returns:
    """

    def _cache_controller(viewfunc):
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
        _wrapped_view_func is a function that wraps around a view function to add never cache headers to the response. It takes a request object, variable arguments (*args), and keyword arguments (**kwargs) as input. The view_func is expected to be a view function that returns a response. The function adds never cache headers to the response and returns the modified response.
        
        Parameters:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments
        """

        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response
    return _wrapped_view_func
ever_cache_headers(response)
        return response
    return _wrapped_view_func
