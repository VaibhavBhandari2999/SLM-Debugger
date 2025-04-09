"""
The provided Python file contains two custom Django forms: `AdminAuthenticationForm` and `AdminPasswordChangeForm`. These forms extend the built-in `AuthenticationForm` and `PasswordChangeForm` from Django's authentication framework, respectively. 

**Key Components:**
1. **AdminAuthenticationForm**: 
   - Inherits from `AuthenticationForm`.
   - Customizes the error messages to specifically mention that only staff accounts can log in.
   - Overrides the `confirm_login_allowed` method to enforce that only staff users are allowed to log in, raising a `ValidationError` otherwise.

2. **AdminPasswordChangeForm**: 
   - Inherits from `PasswordChangeForm`.
   - Adds a `required_css_class` attribute to apply specific CSS styling.

**
"""
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.
    """
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        """
        Confirms that the given user is allowed to log in. This is called each time
        ``authenticate`` is called with a given user. By default, disables login for
        non-staff users. Raises a ValidationError if the login is not allowed.
        
        Args:
        user (User): The user object to be authenticated.
        
        Raises:
        ValidationError: If the user is not staff.
        """

        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class AdminPasswordChangeForm(PasswordChangeForm):
    required_css_class = 'required'
