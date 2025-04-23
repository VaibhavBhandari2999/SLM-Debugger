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
        Clean the form data.
        
        This method is called to check the cleaned data after the form is submitted. It ensures that the 'confirm' field is present in the cleaned data. If the 'confirm' field is missing, a ValidationError is raised.
        
        Parameters:
        None
        
        Returns:
        dict: The cleaned data if 'confirm' is present.
        
        Raises:
        forms.ValidationError: If the 'confirm' field is missing.
        
        Note:
        This method is a part of a Django form and is intended to
        """

        cleaned_data = super().clean()
        if "confirm" not in cleaned_data:
            raise forms.ValidationError("You must confirm the delete.")
