from django import forms

from .models import Author


class AuthorForm(forms.ModelForm):
    name = forms.CharField()
    slug = forms.SlugField()

    class Meta:
        model = Author
        fields = ["name", "slug"]


class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class ConfirmDeleteForm(forms.Form):
    confirm = forms.BooleanField()

    def clean(self):
        """
        Method to clean the form data before validation.
        
        This method ensures that the form data is cleaned and validated before proceeding with any further processing. It checks if the 'confirm' field is present in the cleaned data. If the 'confirm' field is not present, a ValidationError is raised indicating that the user must confirm the delete action.
        
        Parameters:
        None (it relies on the super().clean() method to get the form data)
        
        Returns:
        cleaned_data (dict): The cleaned form data.
        
        Raises
        """

        cleaned_data = super().clean()
        if "confirm" not in cleaned_data:
            raise forms.ValidationError("You must confirm the delete.")
