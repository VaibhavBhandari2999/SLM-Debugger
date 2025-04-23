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
        
        This is an override of the original method to add additional validation.
        If the user is not a staff member, a ValidationError is raised with a specific error message.
        
        Parameters:
        user (User): The user object to be validated.
        
        Returns:
        None: This method does not return any value.
        
        Raises:
        ValidationError: If the user is not a staff member, with a message indicating the login is invalid.
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
