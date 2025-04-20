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
        Method to clean the form data before saving.
        
        This method ensures that the form data is valid before it is saved. It checks if the 'confirm' field is present in the cleaned data. If the 'confirm' field is not present, it raises a ValidationError.
        
        Parameters:
        None (it uses the `cleaned_data` attribute of the form)
        
        Returns:
        cleaned_data (dict): The cleaned form data.
        
        Raises:
        forms.ValidationError: If the 'confirm' field is not present in
        """

        cleaned_data = super().clean()
        if "confirm" not in cleaned_data:
            raise forms.ValidationError("You must confirm the delete.")
