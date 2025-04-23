from unittest import TestCase

from django.core.exceptions import ValidationError
from django.db import models


class ValidationMessagesTest(TestCase):
    def _test_validation_messages(self, field, value, expected):
        """
        Tests the validation messages for a given field.
        
        This function is used to validate a field with a specific value and checks if the error messages match the expected ones.
        
        Parameters:
        field (Field): The field to be validated.
        value (Any): The value to be used for validation.
        expected (list): The expected error messages.
        
        Raises:
        ValidationError: If the validation fails and the error messages do not match the expected ones.
        
        Returns:
        None
        """

        with self.assertRaises(ValidationError) as cm:
            field.clean(value, None)
        self.assertEqual(cm.exception.messages, expected)

    def test_autofield_field_raises_error_message(self):
        f = models.AutoField(primary_key=True)
        self._test_validation_messages(f, "fõo", ["“fõo” value must be an integer."])

    def test_integer_field_raises_error_message(self):
        f = models.IntegerField()
        self._test_validation_messages(f, "fõo", ["“fõo” value must be an integer."])

    def test_boolean_field_raises_error_message(self):
        """
        Tests the validation of a BooleanField in Django models.
        
        This function validates that a BooleanField raises the correct error message
        when provided with an invalid value. The function takes a BooleanField instance
        as input and checks if it raises the expected error message when passed a value
        that is not a boolean.
        
        Parameters:
        f (BooleanField): The BooleanField instance to be tested.
        
        Returns:
        None: This function asserts that the error message is as expected and does
        not return any value
        """

        f = models.BooleanField()
        self._test_validation_messages(
            f, "fõo", ["“fõo” value must be either True or False."]
        )

    def test_nullable_boolean_field_raises_error_message(self):
        f = models.BooleanField(null=True)
        self._test_validation_messages(
            f, "fõo", ["“fõo” value must be either True, False, or None."]
        )

    def test_float_field_raises_error_message(self):
        f = models.FloatField()
        self._test_validation_messages(f, "fõo", ["“fõo” value must be a float."])

    def test_decimal_field_raises_error_message(self):
        f = models.DecimalField()
        self._test_validation_messages(
            f, "fõo", ["“fõo” value must be a decimal number."]
        )

    def test_null_boolean_field_raises_error_message(self):
        f = models.BooleanField(null=True)
        self._test_validation_messages(
            f, "fõo", ["“fõo” value must be either True, False, or None."]
        )

    def test_date_field_raises_error_message(self):
        f = models.DateField()
        self._test_validation_messages(
            f,
            "fõo",
            [
                "“fõo” value has an invalid date format. It must be in YYYY-MM-DD "
                "format."
            ],
        )
        self._test_validation_messages(
            f,
            "aaaa-10-10",
            [
                "“aaaa-10-10” value has an invalid date format. It must be in "
                "YYYY-MM-DD format."
            ],
        )
        self._test_validation_messages(
            f,
            "2011-13-10",
            [
                "“2011-13-10” value has the correct format (YYYY-MM-DD) but it is an "
                "invalid date."
            ],
        )
        self._test_validation_messages(
            f,
            "2011-10-32",
            [
                "“2011-10-32” value has the correct format (YYYY-MM-DD) but it is an "
                "invalid date."
            ],
        )

    def test_datetime_field_raises_error_message(self):
        f = models.DateTimeField()
        # Wrong format
        self._test_validation_messages(
            f,
            "fõo",
            [
                "“fõo” value has an invalid format. It must be in "
                "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format."
            ],
        )
        # Correct format but invalid date
        self._test_validation_messages(
            f,
            "2011-10-32",
            [
                "“2011-10-32” value has the correct format (YYYY-MM-DD) but it is an "
                "invalid date."
            ],
        )
        # Correct format but invalid date/time
        self._test_validation_messages(
            f,
            "2011-10-32 10:10",
            [
                "“2011-10-32 10:10” value has the correct format "
                "(YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]) but it is an invalid date/time."
            ],
        )

    def test_time_field_raises_error_message(self):
        """
        Tests the validation of a TimeField in a Django model.
        
        This function checks the validation behavior of a Django TimeField. It tests two scenarios:
        1. Validation of a time field with an incorrect format.
        2. Validation of a time field with a correct format but an invalid time.
        
        Parameters:
        f (models.TimeField): The TimeField instance to be tested.
        
        Returns:
        None: This function does not return anything. It tests the validation messages and asserts their correctness.
        
        Test Cases:
        -
        """

        f = models.TimeField()
        # Wrong format
        self._test_validation_messages(
            f,
            "fõo",
            [
                "“fõo” value has an invalid format. It must be in HH:MM[:ss[.uuuuuu]] "
                "format."
            ],
        )
        # Correct format but invalid time
        self._test_validation_messages(
            f,
            "25:50",
            [
                "“25:50” value has the correct format (HH:MM[:ss[.uuuuuu]]) but it is "
                "an invalid time."
            ],
        )
    ],
        )
