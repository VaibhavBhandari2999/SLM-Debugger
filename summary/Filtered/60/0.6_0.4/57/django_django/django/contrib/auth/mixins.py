from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import resolve_url


class AccessMixin:
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__)
            )
        return str(login_url)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self):
        """
        Function to handle permission denied or redirect to login if user is not authenticated.
        
        Parameters:
        self (object): The current instance of the class, which should have the following attributes/methods:
        - raise_exception (bool): Whether to raise a PermissionDenied exception if the user is not authenticated.
        - request (HttpRequest): The current HTTP request.
        - get_permission_denied_message () -> str: Method to get the message for permission denied.
        - get_login_url () -> str: Method
        """

        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())

        path = self.request.build_absolute_uri()
        resolved_login_url = resolve_url(self.get_login_url())
        # If the login url is the same scheme and net location then use the
        # path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (
            (not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)
        ):
            path = self.request.get_full_path()
        return redirect_to_login(
            path,
            resolved_login_url,
            self.get_redirect_field_name(),
        )


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        """
        dispatch(request, *args, **kwargs)
        -------------------------------------------------------------------
        Dispatches the request to the appropriate handler method.
        
        Parameters:
        - request: The HTTP request object.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.
        
        Returns:
        - The response from the appropriate handler method.
        
        Note:
        - If the user is not authenticated, the function calls `handle_no_permission()` and returns its result.
        - Otherwise, it calls the superclass's `dispatch` method with the provided arguments.
        """

        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(AccessMixin):
    """Verify that the current user has all specified permissions."""
    permission_required = None

    def get_permission_required(self):
        """
        Override this method to override the permission_required attribute.
        Must return an iterable.
        """
        if self.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request to the appropriate handler. If the user does not have permission, it handles the no permission case. Otherwise, it calls the superclass's dispatch method.
        
        Parameters:
        request (HttpRequest): The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        HttpResponse: The HTTP response object after processing the request.
        If the user lacks permission, it returns the result of handle_no_permission().
        """

        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserPassesTestMixin(AccessMixin):
    """
    Deny a request with a permission error if the test_func() method returns
    False.
    """

    def test_func(self):
        """
        test_func(self)
        
        Summary:
        Raises a NotImplementedError if the test_func() method is not implemented in the derived class.
        
        Parameters:
        self (object): The instance of the class that is calling this method.
        
        Returns:
        None: This method does not return any value. It raises an exception if the method is not implemented.
        
        Raises:
        NotImplementedError: If the test_func() method is not implemented in the derived class.
        
        Details:
        This method is intended to be overridden by subclasses. If it
        """

        raise NotImplementedError(
            '{} is missing the implementation of the test_func() method.'.format(self.__class__.__name__)
        )

    def get_test_func(self):
        """
        Override this method to use a different test_func method.
        """
        return self.test_func

    def dispatch(self, request, *args, **kwargs):
        """
        dispatch(request, *args, **kwargs)
        
        This method is a custom dispatch function for handling HTTP requests in a Django view. It first checks if the user passes a specific test defined by `get_test_func()`. If the user does not pass the test, it calls `handle_no_permission()` to handle the permission issue. If the user passes the test, it proceeds to call the superclass's `dispatch` method to process the request.
        
        Parameters:
        - request: The HTTP request object.
        -
        """

        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
