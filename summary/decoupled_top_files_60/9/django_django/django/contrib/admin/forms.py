from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
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
        Function to confirm if a user is allowed to log in.
        
        This function checks if the provided user is a staff member. If not, it raises a ValidationError with a specific error message.
        
        Parameters:
        user (User): The user object to be checked.
        
        Returns:
        None: This function does not return any value. It either allows the login or raises a ValidationError.
        
        Raises:
        forms.ValidationError: If the user is not a staff member, this error is raised with a custom error message.
        
        Notes
        """

        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class AdminPasswordChangeForm(PasswordChangeForm):
    required_css_class = 'required'
