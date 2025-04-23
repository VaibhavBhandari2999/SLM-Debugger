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
        - self: The instance of the form class that this method belongs to.
        
        Returns:
        - username (str): The validated username if it passes the validation.
        
        Raises:
        - ValidationError: If the username is "customform", indicating a custom form error.
        
        This function is typically used in Django forms to ensure that the username field does not contain a specific reserved keyword, in this case,
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
