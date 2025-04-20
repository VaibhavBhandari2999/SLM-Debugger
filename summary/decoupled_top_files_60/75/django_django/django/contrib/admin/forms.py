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
        Confirm that the user is allowed to log in.
        
        This is called by the login view, and by the automatic login machinery.
        
        Parameters:
        user (User): The user to be logged in.
        
        Returns:
        None: This function does not return any value. It raises a ValidationError if the user is not staff.
        
        Raises:
        ValidationError: If the user is not a staff member, this function raises a ValidationError with the message 'Invalid login' and the code 'invalid_login'.
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
