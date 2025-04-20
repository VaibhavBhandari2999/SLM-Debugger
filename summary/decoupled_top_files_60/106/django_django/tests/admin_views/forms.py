from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    class Media:
        css = {"all": ("path/to/media.css",)}

    def clean_username(self):
        """
        Function to clean the username input.
        
        This method ensures that the provided username is valid and does not match a reserved keyword.
        
        Parameters:
        self (Form): The form instance containing the username field.
        
        Returns:
        str: The cleaned username.
        
        Raises:
        ValidationError: If the username is 'customform', indicating a custom form error.
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
