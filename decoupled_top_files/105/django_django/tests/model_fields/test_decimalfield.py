import math
from decimal import Decimal

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import BigD, Foo


class DecimalFieldTests(TestCase):
    def test_to_python(self):
        """
        Converts various types of input to a Decimal object with specified precision. The function handles integers, strings, and floating-point numbers, ensuring they conform to the max_digits and decimal_places constraints defined by the DecimalField model. It also applies rounding according to the ROUND_HALF_EVEN strategy.
        """

        f = models.DecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal("3"))
        self.assertEqual(f.to_python("3.14"), Decimal("3.14"))
        # to_python() converts floats and honors max_digits.
        self.assertEqual(f.to_python(3.1415926535897), Decimal("3.142"))
        self.assertEqual(f.to_python(2.4), Decimal("2.400"))
        # Uses default rounding of ROUND_HALF_EVEN.
        self.assertEqual(f.to_python(2.0625), Decimal("2.062"))
        self.assertEqual(f.to_python(2.1875), Decimal("2.188"))

    def test_invalid_value(self):
        """
        Tests the validation of invalid values for a DecimalField. The function creates a DecimalField with specified max_digits and decimal_places. It then iterates through a list of test values, attempting to clean each one using the field's clean method. If a value is not a valid decimal number, a ValidationError is expected, and the error message includes the invalid value.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `models.DecimalField`: Creates a DecimalField instance with
        """

        field = models.DecimalField(max_digits=4, decimal_places=2)
        msg = "“%s” value must be a decimal number."
        tests = [
            (),
            [],
            {},
            set(),
            object(),
            complex(),
            "non-numeric string",
            b"non-numeric byte-string",
        ]
        for value in tests:
            with self.subTest(value):
                with self.assertRaisesMessage(ValidationError, msg % (value,)):
                    field.clean(value, None)

    def test_default(self):
        f = models.DecimalField(default=Decimal("0.00"))
        self.assertEqual(f.get_default(), Decimal("0.00"))

    def test_get_prep_value(self):
        """
        Tests the get_prep_value method of a DecimalField.
        
        This method is responsible for preparing the value for database storage.
        It handles None values by returning None and converts string representations
        of decimals into Decimal objects.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Invoked:
        - get_prep_value: The method being tested, which prepares the value for database storage.
        
        Important Variables:
        - f: An instance of models.DecimalField with max_digits set to 5
        """

        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertIsNone(f.get_prep_value(None))
        self.assertEqual(f.get_prep_value("2.4"), Decimal("2.4"))

    def test_filter_with_strings(self):
        """
        Should be able to filter decimal fields using strings (#8023).
        """
        foo = Foo.objects.create(a="abc", d=Decimal("12.34"))
        self.assertEqual(list(Foo.objects.filter(d="12.34")), [foo])

    def test_save_without_float_conversion(self):
        """
        Ensure decimals don't go through a corrupting float conversion during
        save (#5079).
        """
        bd = BigD(d="12.9")
        bd.save()
        bd = BigD.objects.get(pk=bd.pk)
        self.assertEqual(bd.d, Decimal("12.9"))

    def test_save_nan_invalid(self):
        """
        Tests saving invalid 'nan' values to the BigD model.
        
        This function checks that attempting to save 'nan' (Not a Number) values to the `BigD` model results in a `ValidationError` being raised with the message "“nan” value must be a decimal number." The function uses the following key components:
        - `float("nan")`: Represents a NaN value as a floating-point number.
        - `math.nan`: Represents a NaN value from the `math`
        """

        msg = "“nan” value must be a decimal number."
        for value in [float("nan"), math.nan, "nan"]:
            with self.subTest(value), self.assertRaisesMessage(ValidationError, msg):
                BigD.objects.create(d=value)

    def test_save_inf_invalid(self):
        """
        Tests the validation of infinite values for the `BigD` model's decimal field.
        
        This function checks that creating instances of the `BigD` model with infinite
        values (positive or negative) raises a `ValidationError` with the appropriate
        error message. It uses the `float`, `math`, and `assertRaisesMessage` functions
        to validate the behavior.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If an infinite value is
        """

        msg = "“inf” value must be a decimal number."
        for value in [float("inf"), math.inf, "inf"]:
            with self.subTest(value), self.assertRaisesMessage(ValidationError, msg):
                BigD.objects.create(d=value)
        msg = "“-inf” value must be a decimal number."
        for value in [float("-inf"), -math.inf, "-inf"]:
            with self.subTest(value), self.assertRaisesMessage(ValidationError, msg):
                BigD.objects.create(d=value)

    def test_fetch_from_db_without_float_rounding(self):
        """
        Tests fetching a BigD object from the database without float rounding. Creates a BigD object with a specific decimal value, refreshes it from the database, and asserts that the retrieved decimal value remains unchanged.
        """

        big_decimal = BigD.objects.create(d=Decimal(".100000000000000000000000000005"))
        big_decimal.refresh_from_db()
        self.assertEqual(big_decimal.d, Decimal(".100000000000000000000000000005"))

    def test_lookup_really_big_value(self):
        """
        Really big values can be used in a filter statement.
        """
        # This should not crash.
        Foo.objects.filter(d__gte=100000000000)

    def test_max_digits_validation(self):
        """
        Validates that the input value does not exceed the specified maximum digits for a DecimalField.
        
        Args:
        self: The instance of the test case.
        field (models.DecimalField): The DecimalField with a defined max_digits attribute.
        expected_message (str): The expected error message when the validation fails.
        
        Raises:
        ValidationError: If the input value exceeds the maximum digits allowed by the field.
        
        Returns:
        None: The function does not return any value, but raises an exception
        """

        field = models.DecimalField(max_digits=2)
        expected_message = validators.DecimalValidator.messages["max_digits"] % {
            "max": 2
        }
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(100, None)

    def test_max_decimal_places_validation(self):
        """
        Validates that a DecimalField does not exceed the maximum allowed decimal places.
        
        Args:
        field (models.DecimalField): The DecimalField instance being validated.
        value (Decimal): The value to be cleaned and validated.
        
        Raises:
        ValidationError: If the value exceeds the maximum decimal places specified.
        
        Important Functions:
        - `clean`: Cleans and validates the given value.
        - `DecimalValidator.messages["max_decimal_places"]`: Provides the error message template for maximum decimal places validation.
        """

        field = models.DecimalField(decimal_places=1)
        expected_message = validators.DecimalValidator.messages[
            "max_decimal_places"
        ] % {"max": 1}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal("0.99"), None)

    def test_max_whole_digits_validation(self):
        """
        Validates that a DecimalField does not exceed the maximum number of whole digits.
        
        Args:
        field (models.DecimalField): The DecimalField instance being validated.
        max_digits (int): The maximum total number of digits allowed in the field.
        decimal_places (int): The number of decimal places allowed in the field.
        
        Raises:
        ValidationError: If the value exceeds the maximum number of whole digits.
        
        Example:
        >>> field = models.DecimalField(max_digits=3, decimal_places=1
        """

        field = models.DecimalField(max_digits=3, decimal_places=1)
        expected_message = validators.DecimalValidator.messages["max_whole_digits"] % {
            "max": 2
        }
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal("999"), None)

    def test_roundtrip_with_trailing_zeros(self):
        """Trailing zeros in the fractional part aren't truncated."""
        obj = Foo.objects.create(a="bar", d=Decimal("8.320"))
        obj.refresh_from_db()
        self.assertEqual(obj.d.compare_total(Decimal("8.320")), Decimal("0"))
