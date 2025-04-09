import unittest
from decimal import Decimal

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.test import TestCase

from .models import BigD, Foo


class DecimalFieldTests(TestCase):

    def test_to_python(self):
        """
        Converts various types of input to a Decimal object, ensuring that the result adheres to the specified max_digits and decimal_places constraints. The function supports converting integers, strings, and floats to Decimal objects, applying rounding based on the given precision, and raising a ValidationError if the input is not a valid decimal number.
        
        Args:
        value (Union[int, str, float]): The input value to be converted to a Decimal object.
        
        Returns:
        Decimal: The converted Decimal object.
        
        Raises
        """

        f = models.DecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal('3'))
        self.assertEqual(f.to_python('3.14'), Decimal('3.14'))
        # to_python() converts floats and honors max_digits.
        self.assertEqual(f.to_python(3.1415926535897), Decimal('3.142'))
        self.assertEqual(f.to_python(2.4), Decimal('2.400'))
        # Uses default rounding of ROUND_HALF_EVEN.
        self.assertEqual(f.to_python(2.0625), Decimal('2.062'))
        self.assertEqual(f.to_python(2.1875), Decimal('2.188'))
        msg = '“abc” value must be a decimal number.'
        with self.assertRaisesMessage(ValidationError, msg):
            f.to_python('abc')

    def test_default(self):
        f = models.DecimalField(default=Decimal('0.00'))
        self.assertEqual(f.get_default(), Decimal('0.00'))

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
        - Decimal: The class used to convert string representations into Decimal objects.
        
        Important Variables:
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

    @unittest.skipIf(connection.vendor == 'sqlite', 'SQLite stores values rounded to 15 significant digits.')
    def test_fetch_from_db_without_float_rounding(self):
        """
        Tests fetching a BigD object from the database without float rounding. Creates a BigD object with a specific decimal value, refreshes it from the database, and asserts that the retrieved decimal value remains unchanged.
        """

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
        """
        Validates that a DecimalField does not exceed the specified max_digits value.
        
        Args:
        field (DecimalField): The DecimalField instance being validated.
        expected_message (str): The expected error message if validation fails.
        
        Raises:
        ValidationError: If the input value exceeds the max_digits limit.
        
        Usage:
        This function is used to ensure that the input value for a DecimalField does not have more digits than the specified maximum. It raises a ValidationError with a specific error message if the
        """

        field = models.DecimalField(max_digits=2)
        expected_message = validators.DecimalValidator.messages['max_digits'] % {'max': 2}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(100, None)

    def test_max_decimal_places_validation(self):
        """
        Validates that a DecimalField does not exceed the maximum allowed decimal places.
        
        Args:
        field (models.DecimalField): The DecimalField instance being validated.
        expected_message (str): The expected error message if the validation fails.
        
        Raises:
        ValidationError: If the Decimal value has more decimal places than allowed by the field.
        
        Example:
        >>> field = models.DecimalField(decimal_places=1)
        >>> expected_message = validators.DecimalValidator.messages['max_decimal_places'] % {'max': 1
        """

        field = models.DecimalField(decimal_places=1)
        expected_message = validators.DecimalValidator.messages['max_decimal_places'] % {'max': 1}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal('0.99'), None)

    def test_max_whole_digits_validation(self):
        """
        Validates that the whole part of a Decimal value does not exceed the specified maximum digits.
        
        Args:
        field (models.DecimalField): The Decimal field instance with defined max_digits and decimal_places.
        expected_message (str): The expected error message format.
        
        Raises:
        ValidationError: If the whole part of the Decimal value exceeds the maximum allowed digits.
        
        Usage:
        This function is used to ensure that the whole part of a Decimal value does not exceed the specified maximum digits. It takes
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
