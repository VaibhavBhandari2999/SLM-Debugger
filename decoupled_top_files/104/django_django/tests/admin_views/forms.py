from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    class Media:
        css = {"all": ("path/to/media.css",)}

    def clean_username(self):
        """
        Validates the username field in a form. If the username is 'customform', raises a ValidationError with the message 'custom form error'. Returns the cleaned username.
        
        Args:
        self: The form instance.
        
        Returns:
        str: The cleaned username.
        
        Raises:
        ValidationError: If the username is 'customform'.
        """

        username = self.cleaned_data.get("username")
        if username == "customform":
            raise ValidationError("custom form error")
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ["path/to/media.js"]
