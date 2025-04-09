import unittest

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, models
from django.test import SimpleTestCase, TestCase

from .models import (
    BigIntegerModel, IntegerModel, PositiveBigIntegerModel,
    PositiveIntegerModel, PositiveSmallIntegerModel, SmallIntegerModel,
)


class IntegerFieldTests(TestCase):
    model = IntegerModel
    documented_range = (-2147483648, 2147483647)

    @property
    def backend_range(self):
        """
        Generates a range of values based on the internal type of a model field.
        
        Args:
        self: The instance of the class containing the model.
        
        Returns:
        A tuple representing the range of values for the specified field's internal type.
        
        Notes:
        - Utilizes `model._meta.get_field('value')` to retrieve the field object.
        - Determines the internal type of the field using `field.get_internal_type()`.
        - Calls `connection.ops.integer_field_range(internal
        """

        field = self.model._meta.get_field('value')
        internal_type = field.get_internal_type()
        return connection.ops.integer_field_range(internal_type)

    def test_documented_range(self):
        """
        Values within the documented safe range pass validation, and can be
        saved and retrieved without corruption.
        """
        min_value, max_value = self.documented_range

        instance = self.model(value=min_value)
        instance.full_clean()
        instance.save()
        qs = self.model.objects.filter(value__lte=min_value)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].value, min_value)

        instance = self.model(value=max_value)
        instance.full_clean()
        instance.save()
        qs = self.model.objects.filter(value__gte=max_value)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].value, max_value)

    def test_backend_range_save(self):
        """
        Backend specific ranges can be saved without corruption.
        """
        min_value, max_value = self.backend_range

        if min_value is not None:
            instance = self.model(value=min_value)
            instance.full_clean()
            instance.save()
            qs = self.model.objects.filter(value__lte=min_value)
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].value, min_value)

        if max_value is not None:
            instance = self.model(value=max_value)
            instance.full_clean()
            instance.save()
            qs = self.model.objects.filter(value__gte=max_value)
            self.assertEqual(qs.count(), 1)
            self.assertEqual(qs[0].value, max_value)

    def test_backend_range_validation(self):
        """
        Backend specific ranges are enforced at the model validation level
        (#12030).
        """
        min_value, max_value = self.backend_range

        if min_value is not None:
            instance = self.model(value=min_value - 1)
            expected_message = validators.MinValueValidator.message % {
                'limit_value': min_value,
            }
            with self.assertRaisesMessage(ValidationError, expected_message):
                instance.full_clean()
            instance.value = min_value
            instance.full_clean()

        if max_value is not None:
            instance = self.model(value=max_value + 1)
            expected_message = validators.MaxValueValidator.message % {
                'limit_value': max_value,
            }
            with self.assertRaisesMessage(ValidationError, expected_message):
                instance.full_clean()
            instance.value = max_value
            instance.full_clean()

    def test_redundant_backend_range_validators(self):
        """
        If there are stricter validators than the ones from the database
        backend then the backend validators aren't added.
        """
        min_backend_value, max_backend_value = self.backend_range

        for callable_limit in (True, False):
            with self.subTest(callable_limit=callable_limit):
                if min_backend_value is not None:
                    min_custom_value = min_backend_value + 1
                    limit_value = (lambda: min_custom_value) if callable_limit else min_custom_value
                    ranged_value_field = self.model._meta.get_field('value').__class__(
                        validators=[validators.MinValueValidator(limit_value)]
                    )
                    field_range_message = validators.MinValueValidator.message % {
                        'limit_value': min_custom_value,
                    }
                    with self.assertRaisesMessage(ValidationError, '[%r]' % field_range_message):
                        ranged_value_field.run_validators(min_backend_value - 1)

                if max_backend_value is not None:
                    max_custom_value = max_backend_value - 1
                    limit_value = (lambda: max_custom_value) if callable_limit else max_custom_value
                    ranged_value_field = self.model._meta.get_field('value').__class__(
                        validators=[validators.MaxValueValidator(limit_value)]
                    )
                    field_range_message = validators.MaxValueValidator.message % {
                        'limit_value': max_custom_value,
                    }
                    with self.assertRaisesMessage(ValidationError, '[%r]' % field_range_message):
                        ranged_value_field.run_validators(max_backend_value + 1)

    def test_types(self):
        """
        Tests the type of the 'value' attribute in the model.
        
        This function creates an instance of the model with an integer value,
        checks if the type is correct, saves the instance, and verifies the
        type again after retrieval from the database. It uses the `isinstance`
        function to ensure that the 'value' attribute remains an integer throughout.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `self.model(value=1)`
        """

        instance = self.model(value=1)
        self.assertIsInstance(instance.value, int)
        instance.save()
        self.assertIsInstance(instance.value, int)
        instance = self.model.objects.get()
        self.assertIsInstance(instance.value, int)

    def test_coercing(self):
        """
        Tests the coercion of string values to integers. Creates an instance of the model with value '10', retrieves it, and asserts that its value is coerced to 10 (int).
        """

        self.model.objects.create(value='10')
        instance = self.model.objects.get(value='10')
        self.assertEqual(instance.value, 10)

    def test_invalid_value(self):
        """
        Tests the validation of invalid values for the 'value' field in the model.
        
        This function checks if the model raises appropriate exceptions when
        non-numeric values are passed to the 'value' field during object creation.
        The following types of invalid values are tested:
        - Empty tuple: TypeError
        - Empty list: TypeError
        - Empty dictionary: TypeError
        - Empty set: TypeError
        - Instance of object: TypeError
        - Complex number: TypeError
        -
        """

        tests = [
            (TypeError, ()),
            (TypeError, []),
            (TypeError, {}),
            (TypeError, set()),
            (TypeError, object()),
            (TypeError, complex()),
            (ValueError, 'non-numeric string'),
            (ValueError, b'non-numeric byte-string'),
        ]
        for exception, value in tests:
            with self.subTest(value):
                msg = "Field 'value' expected a number but got %r." % (value,)
                with self.assertRaisesMessage(exception, msg):
                    self.model.objects.create(value=value)


class SmallIntegerFieldTests(IntegerFieldTests):
    model = SmallIntegerModel
    documented_range = (-32768, 32767)


class BigIntegerFieldTests(IntegerFieldTests):
    model = BigIntegerModel
    documented_range = (-9223372036854775808, 9223372036854775807)


class PositiveSmallIntegerFieldTests(IntegerFieldTests):
    model = PositiveSmallIntegerModel
    documented_range = (0, 32767)


class PositiveIntegerFieldTests(IntegerFieldTests):
    model = PositiveIntegerModel
    documented_range = (0, 2147483647)

    @unittest.skipIf(connection.vendor == 'sqlite', "SQLite doesn't have a constraint.")
    def test_negative_values(self):
        """
        Test that negative values are not allowed for the 'value' field in the PositiveIntegerModel.
        
        This test creates an instance of PositiveIntegerModel with value set to 0, then attempts to decrement the value by 1 using F-expression. The save operation is expected to raise an IntegrityError due to the constraint that the 'value' field cannot be negative.
        """

        p = PositiveIntegerModel.objects.create(value=0)
        p.value = models.F('value') - 1
        with self.assertRaises(IntegrityError):
            p.save()


class PositiveBigIntegerFieldTests(IntegerFieldTests):
    model = PositiveBigIntegerModel
    documented_range = (0, 9223372036854775807)


class ValidationTests(SimpleTestCase):

    class Choices(models.IntegerChoices):
        A = 1

    def test_integerfield_cleans_valid_string(self):
        f = models.IntegerField()
        self.assertEqual(f.clean('2', None), 2)

    def test_integerfield_raises_error_on_invalid_intput(self):
        """
        Tests that an `IntegerField` raises a `ValidationError` when invalid input is provided.
        
        Args:
        self: The instance of the test case.
        
        Raises:
        ValidationError: If the input is not a valid integer.
        
        Variables:
        f (IntegerField): The integer field to be tested.
        """

        f = models.IntegerField()
        with self.assertRaises(ValidationError):
            f.clean('a', None)

    def test_choices_validation_supports_named_groups(self):
        f = models.IntegerField(choices=(('group', ((10, 'A'), (20, 'B'))), (30, 'C')))
        self.assertEqual(10, f.clean(10, None))

    def test_nullable_integerfield_raises_error_with_blank_false(self):
        """
        Tests that an `IntegerField` with `null=True` and `blank=False` raises a `ValidationError` when cleaned with `None`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the `clean` method does not raise a `ValidationError` when passed `None`.
        
        Functions Used:
        - `models.IntegerField`: Defines the integer field with specified parameters.
        - `clean`: Cleans the value of the field and may raise a `ValidationError`.
        """

        f = models.IntegerField(null=True, blank=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)

    def test_nullable_integerfield_cleans_none_on_null_and_blank_true(self):
        f = models.IntegerField(null=True, blank=True)
        self.assertIsNone(f.clean(None, None))

    def test_integerfield_raises_error_on_empty_input(self):
        """
        Tests that the IntegerField raises a ValidationError when given empty input.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: When cleaning empty or null input.
        
        Functions Used:
        - models.IntegerField
        - clean
        - ValidationError
        
        Input Variables:
        - None
        
        Output Variables:
        - None
        """

        f = models.IntegerField(null=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)
        with self.assertRaises(ValidationError):
            f.clean('', None)

    def test_integerfield_validates_zero_against_choices(self):
        """
        Validates that an integer value of '0' is not accepted when choices are specified for an IntegerField. The function creates an IntegerField with choices set to ((1, 1),) and attempts to clean the value '0'. If the value is invalid according to the choices, a ValidationError is raised.
        
        Args:
        None (The method is a test case and does not take any arguments)
        
        Returns:
        None (Raises a ValidationError if the value '0' is passed)
        """

        f = models.IntegerField(choices=((1, 1),))
        with self.assertRaises(ValidationError):
            f.clean('0', None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.IntegerField(choices=self.Choices.choices)
        self.assertEqual(f.clean('1', None), 1)

    def test_enum_choices_invalid_input(self):
        """
        Tests the validation of invalid inputs for an integer field with choices defined by the Choices enum. The function attempts to clean invalid string values ('A' and '3') and expects ValidationError to be raised in both cases.
        
        Args:
        self: The instance of the test class.
        
        Important Functions:
        - `clean`: Validates the input value.
        - `choices`: Defines the valid choices for the integer field.
        - `ValidationError`: Exception raised when the input is invalid.
        
        Input Variables
        """

        f = models.IntegerField(choices=self.Choices.choices)
        with self.assertRaises(ValidationError):
            f.clean('A', None)
        with self.assertRaises(ValidationError):
            f.clean('3', None)
