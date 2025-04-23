from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import UUIDPK


class UUIDPKForm(forms.ModelForm):
    class Meta:
        model = UUIDPK
        fields = '__all__'


class ModelFormBaseTest(TestCase):
    def test_create_save_error(self):
        """
        Function: test_create_save_error
        
        This function tests the error handling when creating and saving a form with invalid data.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Behavior:
        1. Initializes a UUIDPKForm with empty data.
        2. Checks if the form is not valid.
        3. Asserts that a ValueError is raised with a specific error message indicating that the UUIDPK could not be created due to invalid data.
        
        Raises:
        - ValueError: If the form is valid and the save method is
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        obj = UUIDPK.objects.create(name='foo')
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        """
        Tests the validation of a ModelMultipleChoiceField with a UUID primary key.
        
        This function creates a ModelMultipleChoiceField with a queryset of all UUID primary key objects from the UUIDPK model. It then attempts to clean a list containing an invalid UUID and expects a ValidationError to be raised with the message '“invalid_uuid” is not a valid UUID.'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the cleaning of the invalid UUID does not raise the expected error message
        """

        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(ValidationError, '“invalid_uuid” is not a valid UUID.'):
            f.clean(['invalid_uuid'])
