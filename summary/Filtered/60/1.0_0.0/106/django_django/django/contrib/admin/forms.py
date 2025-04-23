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
        Function: confirm_login_allowed
        
        This method is used to confirm that a user is allowed to log in.
        
        Parameters:
        - user (User): The user object to be checked for login permissions.
        
        Returns:
        - None: This method does not return any value. It raises a ValidationError if the user is not a staff member.
        
        Key Points:
        - It calls the super class's confirm_login_allowed method first.
        - If the user is not a staff member, it raises a ValidationError with a specific error message
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
