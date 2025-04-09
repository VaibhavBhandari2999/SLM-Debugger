from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import UUIDPK


class UUIDPKForm(forms.ModelForm):
    class Meta:
        model = UUIDPK
        fields = "__all__"


class ModelFormBaseTest(TestCase):
    def test_create_save_error(self):
        """
        Summary: This function tests the creation and saving of an invalid UUIDPK form.
        
        Important Functions:
        - `form.is_valid()`: Checks if the form is valid.
        - `form.save()`: Attempts to save the form.
        - `self.assertFalse()`: Asserts that the form is not valid.
        - `self.assertRaisesMessage()`: Raises a ValueError with a specific message if the form is saved.
        
        Input Variables:
        - `form`: An instance of UUID
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Tests updating and saving an object using a UUID primary key form. Ensures that if the form data is invalid, a ValueError is raised with a specific message. The function creates an instance of UUIDPK, initializes a UUIDPKForm with invalid data, checks if the form is not valid, and then attempts to save the form, expecting a ValueError with the message 'The UUIDPK could not be changed because the data didn't validate.'
        """

        obj = UUIDPK.objects.create(name="foo")
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        """
        Tests the validation of a ModelMultipleChoiceField with a UUID primary key.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If an invalid UUID is provided.
        
        Important Functions:
        - `forms.ModelMultipleChoiceField`: Creates a form field for selecting multiple model instances.
        - `clean`: Validates the input data.
        - `assertRaisesMessage`: Asserts that a specific error message is raised during the validation process.
        
        Input Variables:
        -
        """

        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(
            ValidationError, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
