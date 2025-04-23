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
        - None (The function uses internal form validation and does not accept external parameters).
        
        Returns:
        - None (The function performs assertions and raises exceptions, but does not return any value).
        
        Key Steps:
        1. Initializes a UUIDPKForm with empty data.
        2. Checks if the form is not valid.
        3. Constructs an error message indicating the UUIDPK could not be created due
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Tests the update and save functionality of the UUIDPKForm.
        
        This function creates an instance of UUIDPK with the name 'foo', initializes a UUIDPKForm with empty data and the created instance as the instance parameter, and checks if the form is not valid. If the form is valid, it raises an assertion error. It then attempts to save the form, expecting a ValueError to be raised with a specific message indicating that the UUIDPK could not be changed due to invalid data.
        
        Parameters:
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
