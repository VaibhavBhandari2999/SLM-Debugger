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
        - form: The UUIDPKForm instance to be validated and saved.
        
        Returns:
        - None
        
        Key Points:
        - Validates the form data to ensure it is not valid.
        - Raises a ValueError with a specific message if the form is invalid and save is attempted.
        - The message indicates that the UUIDPK could not be created due to invalid data.
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Tests the update and save functionality of the UUIDPKForm.
        
        This function creates an instance of UUIDPK with the name 'foo', then initializes a UUIDPKForm with empty data and the created instance as the instance parameter. It checks if the form is not valid and asserts that a ValueError is raised with a specific message indicating that the UUIDPK could not be changed due to invalid data.
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValueError:
        """

        obj = UUIDPK.objects.create(name='foo')
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(ValidationError, '“invalid_uuid” is not a valid UUID.'):
            f.clean(['invalid_uuid'])
