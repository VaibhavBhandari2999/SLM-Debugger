from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):

    class Media:
        css = {'all': ('path/to/media.css',)}

    def clean_username(self):
        """
        Function to clean the 'username' field in a form.
        
        Parameters:
        - self: The form instance that is calling this method.
        
        Returns:
        - str: The cleaned username.
        
        Raises:
        - ValidationError: If the username is 'customform', indicating a custom form error.
        
        This function is used to validate and clean the 'username' field in a form. It checks if the username is 'customform' and raises a ValidationError if it is. Otherwise, it returns the cleaned username.
        """

        username = self.cleaned_data.get('username')
        if username == 'customform':
            raise ValidationError('custom form error')
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ['path/to/media.js']
