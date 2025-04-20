from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError


class CustomAdminAuthenticationForm(AdminAuthenticationForm):

    class Media:
        css = {'all': ('path/to/media.css',)}

    def clean_username(self):
        """
        Function to clean and validate the 'username' field in a form.
        
        Parameters:
        self (Form): The form instance containing the 'username' field.
        
        Returns:
        str: The cleaned 'username' field value if it passes validation.
        
        Raises:
        ValidationError: If the 'username' field is set to 'customform', indicating a custom form error.
        
        This function is typically used in Django form validation to ensure that the 'username' field does not contain a specific invalid value, in this case
        """

        username = self.cleaned_data.get('username')
        if username == 'customform':
            raise ValidationError('custom form error')
        return username


class MediaActionForm(ActionForm):
    class Media:
        js = ['path/to/media.js']
