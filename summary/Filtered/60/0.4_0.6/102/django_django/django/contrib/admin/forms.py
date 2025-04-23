from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.
    """

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _(
            "Please enter the correct %(username)s and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = "required"

    def confirm_login_allowed(self, user):
        """
        Confirm that the user is allowed to log in.
        
        This is an abstract method that should be overridden to implement
        authentication-specific user validation. If the login is not
        allowed, a ValidationError should be raised with an appropriate
        error message.
        
        Parameters:
        user (User): The user object to be authenticated.
        
        Returns:
        None
        
        Raises:
        ValidationError: If the user is not allowed to log in.
        """

        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
                params={"username": self.username_field.verbose_name},
            )


class AdminPasswordChangeForm(PasswordChangeForm):
    required_css_class = "required"
