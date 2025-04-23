from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    class Media:
        css = {"all": ("path/to/media.css",)}

    def clean_username(self):
        """
        Function: clean_username
        Summary: Validates the provided username to ensure it does not match a reserved keyword.
        Parameters:
        - self: The instance of the form class.
        Returns:
        - username: The validated username if it does not match the reserved keyword "customform".
        Raises:
        - ValidationError: If the username is "customform", indicating a custom form error.
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
