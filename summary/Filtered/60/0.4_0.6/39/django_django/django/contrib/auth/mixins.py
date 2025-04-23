from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


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
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
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
        Generate a Python docstring for the provided function.
        
        This function raises a `NotImplementedError` if the `test_func` method is not implemented in a subclass. It is intended to ensure that any subclass of the class containing this method provides its own implementation.
        
        Parameters:
        self (object): The instance of the class that is expected to implement the `test_func` method.
        
        Returns:
        None: This function does not return any value. It raises an exception if the method is not implemented.
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
        Method: dispatch
        Summary: This method is a part of a Django view class and is responsible for handling incoming HTTP requests. It first checks if the user meets a certain test condition specified by `get_test_func()`. If the user does not meet the condition, it calls `handle_no_permission()` to handle the permission issue. Otherwise, it proceeds to call the superclass's `dispatch` method to process the request.
        
        Parameters:
        - request: The HTTP request object that contains information about the incoming
        """

        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
