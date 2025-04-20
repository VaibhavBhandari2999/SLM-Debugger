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

    @wraps(view_func)
    def wrapper_view(*args, **kwargs):
        """
        Wrapper function for a view function.
        
        This function wraps a view function to ensure that the response includes an "X-Frame-Options" header set to "DENY". If the header is not already present in the response, it is added.
        
        Parameters:
        *args: Variable length argument list to be passed to the view function.
        **kwargs: Arbitrary keyword arguments to be passed to the view function.
        
        Returns:
        A response object with the "X-Frame-Options" header set to
        """

        resp = view_func(*args, **kwargs)
        if resp.get("X-Frame-Options") is None:
            resp["X-Frame-Options"] = "DENY"
        return resp

    return wrapper_view


def xframe_options_sameorigin(view_func):
    """
    Modify a view function so its response has the X-Frame-Options HTTP
    header set to 'SAMEORIGIN' as long as the response doesn't already have
    that header set. Usage:

    @xframe_options_sameorigin
    def some_view(request):
        ...
    """

    @wraps(view_func)
    def wrapper_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)
        if resp.get("X-Frame-Options") is None:
            resp["X-Frame-Options"] = "SAMEORIGIN"
        return resp

    return wrapper_view


def xframe_options_exempt(view_func):
    """
    Modify a view function by setting a response variable that instructs
    XFrameOptionsMiddleware to NOT set the X-Frame-Options HTTP header. Usage:

    @xframe_options_exempt
    def some_view(request):
        ...
    """

    @wraps(view_func)
    def wrapper_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)
        resp.xframe_options_exempt = True
        return resp

    return wrapper_view
