from decimal import Decimal

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import BigD, Foo


class DecimalFieldTests(TestCase):

    def test_to_python(self):
        f = models.DecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal('3'))
        self.assertEqual(f.to_python('3.14'), Decimal('3.14'))
        # to_python() converts floats and honors max_digits.
        self.assertEqual(f.to_python(3.1415926535897), Decimal('3.142'))
        self.assertEqual(f.to_python(2.4), Decimal('2.400'))
        # Uses default rounding of ROUND_HALF_EVEN.
        self.assertEqual(f.to_python(2.0625), Decimal('2.062'))
        self.assertEqual(f.to_python(2.1875), Decimal('2.188'))

    def test_invalid_value(self):
        """
        Tests the validation of invalid values for a DecimalField.
        
        This function checks whether the provided values are correctly identified as invalid for a DecimalField. The key parameters are:
        - `field`: A DecimalField instance with a maximum of 4 digits and 2 decimal places.
        - `msg`: A string message used to format the error message when a validation error occurs.
        
        The function iterates over a list of test values, each of which is expected to raise a ValidationError with the specified message. The test
        """

        field = models.DecimalField(max_digits=4, decimal_places=2)
        msg = '“%s” value must be a decimal number.'
        tests = [
            (),
            [],
            {},
            set(),
            object(),
            complex(),
            'non-numeric string',
            b'non-numeric byte-string',
        ]
        for value in tests:
            with self.subTest(value):
                with self.assertRaisesMessage(ValidationError, msg % (value,)):
                    field.clean(value, None)

    def test_default(self):
        f = models.DecimalField(default=Decimal('0.00'))
        self.assertEqual(f.get_default(), Decimal('0.00'))

    def test_get_prep_value(self):
        """
        Tests the get_prep_value method for a DecimalField.
        
        Parameters:
        - f (models.DecimalField): The DecimalField instance with max_digits=5 and decimal_places=1.
        
        Returns:
        - None: The method returns None when the input is None.
        - Decimal: The method returns a Decimal object when a string representation of a number is provided.
        
        Key Points:
        - The method handles None input by returning None.
        - The method converts a string representation of a number to a Decimal object.
        """

        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertIsNone(f.get_prep_value(None))
        self.assertEqual(f.get_prep_value('2.4'), Decimal('2.4'))

    def test_filter_with_strings(self):
        """
        Should be able to filter decimal fields using strings (#8023).
        """
        foo = Foo.objects.create(a='abc', d=Decimal('12.34'))
        self.assertEqual(list(Foo.objects.filter(d='12.34')), [foo])

    def test_save_without_float_conversion(self):
        """
        Ensure decimals don't go through a corrupting float conversion during
        save (#5079).
        """
        bd = BigD(d='12.9')
        bd.save()
        bd = BigD.objects.get(pk=bd.pk)
        self.assertEqual(bd.d, Decimal('12.9'))

    def test_fetch_from_db_without_float_rounding(self):
        big_decimal = BigD.objects.create(d=Decimal('.100000000000000000000000000005'))
        big_decimal.refresh_from_db()
        self.assertEqual(big_decimal.d, Decimal('.100000000000000000000000000005'))

    def test_lookup_really_big_value(self):
        """
        Really big values can be used in a filter statement.
        """
        # This should not crash.
        Foo.objects.filter(d__gte=100000000000)

    def test_max_digits_validation(self):
        field = models.DecimalField(max_digits=2)
        expected_message = validators.DecimalValidator.messages['max_digits'] % {'max': 2}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(100, None)

    def test_max_decimal_places_validation(self):
        field = models.DecimalField(decimal_places=1)
        expected_message = validators.DecimalValidator.messages['max_decimal_places'] % {'max': 1}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal('0.99'), None)

    def test_max_whole_digits_validation(self):
        """
        Validate the maximum number of whole digits in a Decimal field.
        
        This function tests the validation of a Decimal field to ensure it does not exceed the specified maximum number of whole digits. The function takes a Decimal instance as input and raises a ValidationError if the number of whole digits exceeds the allowed limit.
        
        Parameters:
        field (DecimalField): The DecimalField instance to be validated.
        value (Decimal): The Decimal value to be checked.
        
        Returns:
        None: The function does not return anything. It either
        """

        field = models.DecimalField(max_digits=3, decimal_places=1)
        expected_message = validators.DecimalValidator.messages['max_whole_digits'] % {'max': 2}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal('999'), None)

    def test_roundtrip_with_trailing_zeros(self):
        """Trailing zeros in the fractional part aren't truncated."""
        obj = Foo.objects.create(a='bar', d=Decimal('8.320'))
        obj.refresh_from_db()
        self.assertEqual(obj.d.compare_total(Decimal('8.320')), Decimal('0'))
