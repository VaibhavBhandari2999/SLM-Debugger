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
        form = UUIDPKForm({})
        self.assertFalse(form.is_valid())
        msg = "The UUIDPK could not be created because the data didn't validate."
        with self.assertRaisesMessage(ValueError, msg):
            form.save()

    def test_update_save_error(self):
        """
        Test the update and save functionality of the UUIDPKForm.
        
        This function tests the behavior of the UUIDPKForm when trying to update and save an existing UUIDPK object. The object is initially created with a name 'foo'. A form is then instantiated with empty data and the existing object as an instance. The form is expected to be invalid due to missing data. The function asserts that the form is not valid and attempts to save the form, which should raise a ValueError with a specific message indicating that
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
valid UUID.'):
            f.clean(['invalid_uuid'])
