from django import forms

from .models import Author


class AuthorForm(forms.ModelForm):
    name = forms.CharField()
    slug = forms.SlugField()

    class Meta:
        model = Author
        fields = ['name', 'slug']


class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class ConfirmDeleteForm(forms.Form):
    confirm = forms.BooleanField()

    def clean(self):
        """
        clean(self)
        
        This method is a custom validation function for a Django form. It ensures that the 'confirm' field is present in the cleaned data before proceeding. If the 'confirm' field is missing, a ValidationError is raised.
        
        Parameters:
        None
        
        Returns:
        cleaned_data (dict): The cleaned data dictionary, which is the result of the form's validation process.
        
        Raises:
        forms.ValidationError: If the 'confirm' field is not present in the cleaned data, a validation error
        """

        cleaned_data = super().clean()
        if 'confirm' not in cleaned_data:
            raise forms.ValidationError('You must confirm the delete.')
