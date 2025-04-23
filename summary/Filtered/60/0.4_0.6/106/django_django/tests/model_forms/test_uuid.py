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
        
        This function tests the error handling when attempting to save an invalid form with a UUIDPK.
        
        Parameters:
        - None (The function uses internal form creation and validation)
        
        Returns:
        - None (The function raises a ValueError with a specific message if the form is invalid and save is attempted)
        
        Key Points:
        - A UUIDPKForm is instantiated with empty data.
        - The form's validity is checked using `form.is_valid()`.
        - If the form is invalid, a ValueError
        """

        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Tests the update and save functionality of a UUIDPKForm.
        
        This function creates a UUIDPK object with the name 'foo', then initializes a UUIDPKForm with no data and the created object as the instance. It checks if the form is not valid and asserts that a ValueError is raised with a specific message when attempting to save the form. The key parameters are:
        - `self`: The test case instance.
        
        The function does not return any value but raises a ValueError with a specific message if the form
        """

        obj = UUIDPK.objects.create(name="foo")
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(
            ValidationError, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
