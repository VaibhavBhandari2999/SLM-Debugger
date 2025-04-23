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
        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Test the update and save functionality of the UUIDPKForm.
        
        This function creates a UUIDPK object with the name 'foo', initializes a UUIDPKForm with an empty dictionary and the created object as the instance, and checks if the form is not valid. If the form is valid, it will raise an assertion error. Then, it attempts to save the form, which should raise a ValueError with a specific message indicating that the UUIDPK could not be changed because the data did not validate.
        
        Parameters:
        """

        obj = UUIDPK.objects.create(name="foo")
        form = UUIDPKForm({}, instance=obj)
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be changed because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_model_multiple_choice_field_uuid_pk(self):
        """
        Tests the validation of a ModelMultipleChoiceField with UUID primary key.
        
        This function creates a ModelMultipleChoiceField for the UUIDPK model and attempts to clean a list containing an invalid UUID. It expects to raise a ValidationError with a specific message.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: If the invalid UUID is not caught and validated correctly.
        
        Key Points:
        - The function uses a ModelMultipleChoiceField with all instances of the UUIDPK model.
        - It attempts to
        """

        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(
            ValidationError, "“invalid_uuid” is not a valid UUID."
        ):
            f.clean(["invalid_uuid"])
