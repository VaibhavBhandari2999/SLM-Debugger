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
        Function: test_create_save_error
        
        This function tests the error handling when attempting to create and save a form with invalid data.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - A UUIDPKForm is instantiated with an empty dictionary.
        - The form's validity is checked using `is_valid()`.
        - If the form is not valid, a custom error message is expected to be raised when `save()` is called.
        - The error message should indicate that the UUIDPK could not be
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        obj = UUIDPK.objects.create(name="foo")
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        """
        Tests the validation of a ModelMultipleChoiceField with a UUID primary key.
        
        This function creates a ModelMultipleChoiceField for the UUIDPK model and attempts to clean a list containing an invalid UUID. It expects to raise a ValidationError with a specific error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the invalid UUID is not properly handled and does not raise the expected error message.
        
        Key Points:
        - The function uses a ModelMultipleChoiceField with all instances of the
        """

        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(
            ValidationError, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
