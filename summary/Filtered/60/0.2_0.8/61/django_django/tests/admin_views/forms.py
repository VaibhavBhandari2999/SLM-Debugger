from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):

    class Media:
        css = {'all': ('path/to/media.css',)}

    def clean_username(self):
        """
        Function to clean and validate the username input.
        
        Parameters:
        self (Form): The form instance containing the username field.
        
        Returns:
        str: The cleaned username if it passes validation.
        
        Raises:
        ValidationError: If the username is 'customform', indicating a custom form error.
        
        This function is used to validate the username field in a form. It checks if the username is 'customform' and raises a ValidationError if it is. Otherwise, it returns the cleaned username.
        """

        username = self.cleaned_data.get('username')
        if username == 'customform':
            raise ValidationError('custom form error')
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ['path/to/media.js']
