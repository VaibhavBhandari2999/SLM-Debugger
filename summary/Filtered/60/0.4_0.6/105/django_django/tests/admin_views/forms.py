from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    class Media:
        css = {"all": ("path/to/media.css",)}

    def clean_username(self):
        """
        Function to clean the username input.
        
        This method is used to validate and clean the username input in a form. It checks if the provided username is "customform". If it is, a ValidationError is raised with the message "custom form error". Otherwise, the username is returned as is.
        
        Parameters:
        self (Form): The form object containing the username input.
        
        Returns:
        str: The cleaned username if it passes the validation.
        
        Raises:
        ValidationError: If the username is "customform".
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
