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
        Test the create_save_error method.
        
        This method tests the behavior of the form when it is not valid and attempts to save. It ensures that the form correctly identifies invalid data and raises a ValueError with a specific message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the form is invalid and save is attempted, the ValueError is raised with a specific message.
        
        Key Points:
        - The form is initialized with empty data.
        - The form's validity is checked.
        - If the
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
        f = forms.ModelMultipleChoiceField(UUIDPK.objects.all())
        with self.assertRaisesMessage(ValidationError, '“invalid_uuid” is not a valid UUID.'):
            f.clean(['invalid_uuid'])
