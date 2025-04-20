import re
from unittest import TestCase

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


class TestFieldWithValidators(TestCase):
    def test_all_errors_get_reported(self):
        """
        Tests the validation of a form with multiple fields and validators.
        
        This function creates a form with three fields: 'full_name', 'string', and 'ignore_case_string'. Each field has its own set of validators. The function then attempts to validate the form with invalid data and checks that the appropriate errors are raised and reported.
        
        Key Parameters:
        - None
        
        Keywords:
        - form: The form instance created for testing.
        - full_name: A field with a CharField that validates if the input is an
        """

        class UserForm(forms.Form):
            full_name = forms.CharField(
                max_length=50,
                validators=[
                    validators.validate_integer,
                    validators.validate_email,
                ]
            )
            string = forms.CharField(
                max_length=50,
                validators=[
                    validators.RegexValidator(
                        regex='^[a-zA-Z]*$',
                        message="Letters only.",
                    )
                ]
            )
            ignore_case_string = forms.CharField(
                max_length=50,
                validators=[
                    validators.RegexValidator(
                        regex='^[a-z]*$',
                        message="Letters only.",
                        flags=re.IGNORECASE,
                    )
                ]
            )

        form = UserForm({
            'full_name': 'not int nor mail',
            'string': '2 is not correct',
            'ignore_case_string': "IgnORE Case strIng",
        })
        with self.assertRaises(ValidationError) as e:
            form.fields['full_name'].clean('not int nor mail')
        self.assertEqual(2, len(e.exception.messages))

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['string'], ["Letters only."])
        self.assertEqual(form.errors['string'], ["Letters only."])

    def test_field_validators_can_be_any_iterable(self):
        """
        Tests that field validators can be any iterable.
        
        This function checks if the validators for a form field can accept any iterable, such as a tuple or list, containing multiple validation functions. The form field 'full_name' is defined with two validators: 'validate_integer' and 'validate_email'. The test case creates an instance of the form with invalid input ('not int nor mail') and expects the form to be invalid, with errors indicating that the input is neither a valid integer nor a valid email address
        """

        class UserForm(forms.Form):
            full_name = forms.CharField(
                max_length=50,
                validators=(
                    validators.validate_integer,
                    validators.validate_email,
                )
            )

        form = UserForm({'full_name': 'not int nor mail'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['full_name'], ['Enter a valid integer.', 'Enter a valid email address.'])
