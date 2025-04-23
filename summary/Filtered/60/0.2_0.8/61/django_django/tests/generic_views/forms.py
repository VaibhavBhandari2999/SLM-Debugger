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
        Method to validate the form data before submission.
        
        This method ensures that the user has confirmed the deletion before proceeding.
        
        Parameters:
        cleaned_data (dict): The cleaned form data.
        
        Returns:
        dict: The cleaned form data if the confirmation is valid, otherwise raises a ValidationError.
        
        Raises:
        ValidationError: If the 'confirm' field is not present in the cleaned data.
        """

        cleaned_data = super().clean()
        if 'confirm' not in cleaned_data:
            raise forms.ValidationError('You must confirm the delete.')
