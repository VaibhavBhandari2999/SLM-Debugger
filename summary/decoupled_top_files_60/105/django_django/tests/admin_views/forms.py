from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    class Media:
        css = {"all": ("path/to/media.css",)}

    def clean_username(self):
        """
        Function to clean and validate the username input.
        
        Args:
        self (Form): The form object containing the username field.
        
        Returns:
        str: The cleaned username if valid.
        
        Raises:
        ValidationError: If the username is 'customform'.
        
        This function is used to validate the username field in a form. It checks if the provided username is 'customform' and raises a ValidationError if it is. If the username is valid, it is returned as a cleaned string.
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
