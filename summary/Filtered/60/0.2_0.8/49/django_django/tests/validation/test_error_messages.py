from unittest import TestCase

from django.core.exceptions import ValidationError
from django.db import models


class ValidationMessagesTest(TestCase):

    def _test_validation_messages(self, field, value, expected):
        """
        Tests the validation messages for a given field.
        
        This function is used to validate a field's clean method and ensure it raises a ValidationError with the expected error messages.
        
        Parameters:
        field (Field): The field instance to test.
        value (Any): The value to be passed to the field's clean method.
        expected (list): A list of expected error messages.
        
        Raises:
        AssertionError: If the error messages do not match the expected ones.
        
        Returns:
        None: This function does not return
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
        f = models.NullBooleanField()
        self._test_validation_messages(f, 'fõo', ['“fõo” value must be either None, True or False.'])

    def test_date_field_raises_error_message(self):
        """
        Test the validation of a DateField in a Django model.
        
        This function tests the validation of a DateField in a Django model. It checks if the field raises the correct error messages for various invalid date formats and values.
        
        Parameters:
        f (models.DateField): The DateField instance to be tested.
        
        Returns:
        None: This function does not return anything. It tests the validation messages and asserts the expected results.
        
        Test Cases:
        - 'fõo': Raises an error message indicating an invalid date
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
        Test the validation of a DateTimeField.
        
        This function tests the validation of a DateTimeField by providing various input values and checking the error messages generated. The function expects a DateTimeField instance as input and validates it against different scenarios.
        
        Parameters:
        f (models.DateTimeField): The DateTimeField instance to be tested.
        
        Test Cases:
        1. Tests if a value with an invalid format raises the correct error message.
        2. Tests if a value with a correct format but an invalid date raises the correct error message.
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
        Tests the behavior of a TimeField in a Django model.
        
        This function validates the TimeField to ensure it raises appropriate error messages for incorrect input formats and invalid times.
        
        Parameters:
        f (models.TimeField): The TimeField instance to test.
        
        Test Cases:
        1. Tests the error message for a wrong format input ('fõo').
        2. Tests the error message for a correct format but invalid time input ('25:50').
        
        Each test case uses the `_test_validation_messages`
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
