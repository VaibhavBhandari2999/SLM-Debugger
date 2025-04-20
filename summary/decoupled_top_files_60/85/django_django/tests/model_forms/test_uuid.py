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
        
        Key Points:
        - A UUIDPKForm is instantiated with an empty dictionary ({}).
        - The form's validity is checked using `form.is_valid()`, which should return False for invalid data.
        - A custom error message is expected to be raised when attempting to save the form, indicating that the UUIDPK could not be created due to
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Tests the update and save functionality of the UUIDPKForm.
        
        This function creates a UUIDPK object with the name 'foo', then initializes a UUIDPKForm with empty data and the created object as the instance. It checks if the form is not valid and expects a ValueError to be raised when attempting to save the form. The error message should indicate that the UUIDPK could not be changed due to invalid data.
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Returns:
        - None
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
