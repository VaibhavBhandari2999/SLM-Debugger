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
        Ensures that the form contains a confirmation of deletion before allowing submission.
        
        This method is called during form validation. It checks if the 'confirm' field is present in the cleaned data. If the 'confirm' field is missing, a ValidationError is raised with the message "You must confirm the delete."
        
        Args:
        None (the method relies on the form's cleaned_data attribute)
        
        Returns:
        cleaned_data (dict): The cleaned form data, potentially modified by the method.
        
        Raises
        """

        cleaned_data = super().clean()
        if "confirm" not in cleaned_data:
            raise forms.ValidationError("You must confirm the delete.")
