"""
```python
"""
from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        """
        Decorator that restricts access to views based on a test function.
        
        The test function should return True if the user is allowed to see the
        view, False otherwise.
        
        Example usage:
        @login_required
        @user_passes_test(lambda u: u.is_staff)
        def my_view(request):
        ...
        """

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            """
            _wrapped_view is a function that checks if the user meets the test condition specified by `test_func`. If the user passes the test, it calls the original view function (`view_func`) with the provided arguments. If the user fails the test, it redirects the user to the login page. The function uses `request.build_absolute_uri()` to get the full URL of the current request, `resolve_url()` to get the absolute URL of the login page, and `redirect_to_login()` to redirect
            """

            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        """
        Check if the given user has the specified permission(s).
        
        Args:
        user: The user object to check permissions for.
        
        Returns:
        bool: True if the user has the required permission(s), False otherwise.
        
        Raises:
        PermissionDenied: If `raise_exception` is set to True and the user does not have the required permission(s).
        
        Notes:
        - The function accepts either a single permission string or a tuple of permission strings.
        - It first checks if the user has
        """

        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)
