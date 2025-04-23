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
        Tests the to_python method of a DecimalField model.
        
        This method converts various types of input into Decimal objects, ensuring that the conversion respects the max_digits and decimal_places constraints. It handles integer, string, float, and specific floating-point values, applying rounding as necessary.
        
        Parameters:
        - f (models.DecimalField): The DecimalField instance with specified max_digits and decimal_places.
        
        Returns:
        - Decimal: The converted Decimal object.
        
        Key Conversions:
        - Integer (3) to Decimal("3")
        - String
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
        msg = "“nan” value must be a decimal number."
        for value in [float("nan"), math.nan, "nan"]:
            with self.subTest(value), self.assertRaisesMessage(ValidationError, msg):
                BigD.objects.create(d=value)

    def test_save_inf_invalid(self):
        """
        Tests the validation of infinite values for the BigD model's decimal field.
        
        This function tests the validation of both positive and negative infinite values for the decimal field of the BigD model. It ensures that attempting to save an infinite value raises a ValidationError with a specific error message.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - None
        
        Raises:
        - ValidationError: If an infinite value is attempted to be saved, the function raises a ValidationError with a specific error
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
        Tests the validation of a DecimalField with a specified max_digits parameter.
        
        This function checks if a DecimalField with a max_digits of 2 raises a ValidationError when a value greater than 99 is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the DecimalField does not raise a ValidationError with the expected message when provided with a value of 100.
        
        Expected Behavior:
        A ValidationError is raised with the message: 'Ensure that there are no more
        """

        field = models.DecimalField(max_digits=2)
        expected_message = validators.DecimalValidator.messages["max_digits"] % {
            "max": 2
        }
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(100, None)

    def test_max_decimal_places_validation(self):
        field = models.DecimalField(decimal_places=1)
        expected_message = validators.DecimalValidator.messages[
            "max_decimal_places"
        ] % {"max": 1}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal("0.99"), None)

    def test_max_whole_digits_validation(self):
        """
        Validate that a Decimal field does not exceed the maximum number of whole digits.
        
        This function tests the validation logic for a Decimal field to ensure it raises a ValidationError if the number of whole digits exceeds the specified maximum.
        
        Parameters:
        None (This function uses an instance method of a Django model field)
        
        Returns:
        None (The function raises a ValidationError if the validation fails)
        
        Raises:
        ValidationError: If the Decimal value has more whole digits than the specified maximum (3 in this case).
        
        Key Points:
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
