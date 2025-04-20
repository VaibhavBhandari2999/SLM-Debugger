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
        Tests the create_save_error method for UUIDPKForm.
        
        This method checks the validation and saving process of a UUIDPKForm. It ensures that the form is not valid when an empty dictionary is passed, and that a ValueError is raised with a specific message when attempting to save the form.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the form is invalid and save is attempted, with a specific error message.
        
        Key Points:
        - The form is expected to be invalid when
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
        
        This function creates a ModelMultipleChoiceField with a queryset of UUIDPK objects. It then attempts to clean a list containing an invalid UUID and expects a ValidationError to be raised with a specific error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the invalid UUID is successfully cleaned, indicating a validation failure.
        
        Key Points:
        - The function uses a ModelMultipleChoiceField with a queryset of UUID
        """

        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(
            ValidationError, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
