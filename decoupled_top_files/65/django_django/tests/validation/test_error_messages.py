"""
This Python file contains unit tests for validating Django model fields. It defines a test class `ValidationMessagesTest` that includes methods to test the validation messages for various types of Django model fields such as AutoField, IntegerField, BooleanField, FloatField, DecimalField, DateField, DateTimeField, and TimeField. Each test method creates an instance of a specific field type, passes a value that should trigger a validation error, and asserts that the error messages returned by the field's `clean` method match the expected error messages. The tests cover common validation scenarios including incorrect data types, invalid formats, and out-of-range values.

The `ValidationMessagesTest` class relies on the `_test_validation_messages` helper function to perform the actual validation and
"""
from unittest import TestCase

from django.core.exceptions import ValidationError
from django.db import models


class ValidationMessagesTest(TestCase):

    def _test_validation_messages(self, field, value, expected):
        """
        Tests the validation messages for a given field.
        
        Args:
        field (Field): The field to test.
        value: The value to be validated.
        expected (list): The expected validation error messages.
        
        Raises:
        ValidationError: If the validation fails and the error messages do not match the expected ones.
        
        Summary:
        This function tests the validation messages of a field by passing a value through its clean method and comparing the resulting error messages with the expected ones. It uses the `clean
        """

        with self.assertRaises(ValidationError) as cm:
            field.clean(value, None)
        self.assertEqual(cm.exception.messages, expected)

    def test_autofield_field_raises_error_message(self):
        f = models.AutoField(primary_key=True)
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be an integer.'])

    def test_integer_field_raises_error_message(self):
        f = models.IntegerField()
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be an integer.'])

    def test_boolean_field_raises_error_message(self):
        f = models.BooleanField()
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be either True or False.'])

    def test_nullable_boolean_field_raises_error_message(self):
        f = models.BooleanField(null=True)
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be either True, False, or None.'])

    def test_float_field_raises_error_message(self):
        f = models.FloatField()
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be a float.'])

    def test_decimal_field_raises_error_message(self):
        f = models.DecimalField()
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be a decimal number.'])

    def test_null_boolean_field_raises_error_message(self):
        f = models.BooleanField(null=True)
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be either True, False, or None.'])

    def test_date_field_raises_error_message(self):
        """
        Tests the validation of a DateField model.
        
        This function validates various date formats and inputs against a DateField model instance `f`. It checks for:
        - Invalid date format: Ensures that non-date strings like 'fõo' raise a specific error message.
        - Incorrect year format: Verifies that dates with incorrect years like 'aaaa-10-10' also raise a specific error message.
        - Incorrect month format: Confirms that dates with incorrect months like '
        """

        f = models.DateField()
        self._test_validation_messages(
            f, 'fõo',
            ['“fõo” value has an invalid date format. It must be in YYYY-MM-DD format.']
        )
        self._test_validation_messages(
            f, 'aaaa-10-10',
            ['“aaaa-10-10” value has an invalid date format. It must be in YYYY-MM-DD format.']
        )
        self._test_validation_messages(
            f, '2011-13-10',
            ['“2011-13-10” value has the correct format (YYYY-MM-DD) but it is an invalid date.']
        )
        self._test_validation_messages(
            f, '2011-10-32',
            ['“2011-10-32” value has the correct format (YYYY-MM-DD) but it is an invalid date.']
        )

    def test_datetime_field_raises_error_message(self):
        """
        Tests the validation of a DateTimeField.
        
        This function validates different inputs against a DateTimeField and checks if the expected error messages are raised.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `_test_validation_messages`: Used to test the validation messages for the given input and expected error message.
        
        Input Variables:
        - `f`: An instance of `models.DateTimeField()` representing the field to be validated.
        
        Output Variables:
        - The function tests various inputs
        """

        f = models.DateTimeField()
        # Wrong format
        self._test_validation_messages(
            f, 'fõo',
            ['“fõo” value has an invalid format. It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.']
        )
        # Correct format but invalid date
        self._test_validation_messages(
            f, '2011-10-32',
            ['“2011-10-32” value has the correct format (YYYY-MM-DD) but it is an invalid date.']
        )
        # Correct format but invalid date/time
        self._test_validation_messages(
            f, '2011-10-32 10:10',
            ['“2011-10-32 10:10” value has the correct format (YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]) '
             'but it is an invalid date/time.']
        )

    def test_time_field_raises_error_message(self):
        """
        Tests the validation of a TimeField model.
        
        This function validates the input against the constraints of a TimeField model.
        It checks for incorrect formats and invalid times, ensuring that only valid time strings are accepted.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - `_test_validation_messages`: Tests the validation messages for the given field and input values.
        
        Important Keywords:
        - TimeField: The model field being tested.
        - Validation Messages: Error messages
        """

        f = models.TimeField()
        # Wrong format
        self._test_validation_messages(
            f, 'fõo',
            ['“fõo” value has an invalid format. It must be in HH:MM[:ss[.uuuuuu]] format.']
        )
        # Correct format but invalid time
        self._test_validation_messages(
            f, '25:50',
            ['“25:50” value has the correct format (HH:MM[:ss[.uuuuuu]]) but it is an invalid time.']
        )
