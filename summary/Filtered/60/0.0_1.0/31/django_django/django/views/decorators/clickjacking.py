from functools import wraps


def xframe_options_deny(view_func):
    """
    Modify a view function so its response has the X-Frame-Options HTTP
    header set to 'DENY' as long as the response doesn't already have that
    header set. Usage:

    @xframe_options_deny
    def some_view(request):
        ...
    """
    def wrapped_view(*args, **kwargs):
        """
        Function to wrap a view function and add the 'X-Frame-Options' header with the value 'DENY' if it is not already present.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        A modified response object with the 'X-Frame-Options' header set to 'DENY' if it was not already present.
        """

        resp = view_func(*args, **kwargs)
        if resp.get('X-Frame-Options') is None:
            resp['X-Frame-Options'] = 'DENY'
        return resp
    return wraps(view_func)(wrapped_view)


def xframe_options_sameorigin(view_func):
    """
    Modify a view function so its response has the X-Frame-Options HTTP
    header set to 'SAMEORIGIN' as long as the response doesn't already have
    that header set. Usage:

    @xframe_options_sameorigin
    def some_view(request):
        ...
    """
    def wrapped_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)
        if resp.get('X-Frame-Options') is None:
            resp['X-Frame-Options'] = 'SAMEORIGIN'
        return resp
    return wraps(view_func)(wrapped_view)


def xframe_options_exempt(view_func):
    """
    Modify a view function by setting a response variable that instructs
    XFrameOptionsMiddleware to NOT set the X-Frame-Options HTTP header. Usage:

    @xframe_options_exempt
    def some_view(request):
        ...
    """
    def wrapped_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)
        resp.xframe_options_exempt = True
        return resp
    return wraps(view_func)(wrapped_view)
**kwargs)
        resp.xframe_options_exempt = True
        return resp
    return wraps(view_func)(wrapped_view)
ns_exempt = True
        return resp
    return wraps(view_func)(wrapped_view)
