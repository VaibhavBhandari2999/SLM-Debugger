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
        Generates the range of values for a backend-specific integer field.
        
        This function retrieves the range of values for an integer field in the database backend. It uses the model's field 'value' to determine the internal type of the field and then calls the `integer_field_range` method of the current database connection's operations class to get the range.
        
        Parameters:
        None
        
        Returns:
        A tuple representing the range of values for the integer field. The tuple contains two elements: the minimum and maximum values
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
        instance = self.model(value=1)
        self.assertIsInstance(instance.value, int)
        instance.save()
        self.assertIsInstance(instance.value, int)
        instance = self.model.objects.get()
        self.assertIsInstance(instance.value, int)

    def test_coercing(self):
        """
        Tests the coercion of string values to integers in a model field.
        
        This function creates a model instance with a string value '10' and retrieves it. It then checks if the value has been coerced to an integer 10.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Attributes:
        - model: The model class being tested.
        - value: The string value '10' that is initially stored in the database.
        
        Assertions:
        - The retrieved instance's value should be equal to
        """

        self.model.objects.create(value='10')
        instance = self.model.objects.get(value='10')
        self.assertEqual(instance.value, 10)

    def test_invalid_value(self):
        """
        Tests the behavior of the model's 'value' field with various invalid inputs.
        
        This function tests the 'value' field of the model to ensure it raises the correct exceptions and error messages for invalid input types. The function iterates through a list of test cases, each containing an expected exception type and a value to test. For each test case, it creates a sub-test to validate that the specified exception is raised with the correct error message.
        
        Parameters:
        - exception (type): The expected exception type
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
        f = models.IntegerField()
        with self.assertRaises(ValidationError):
            f.clean('a', None)

    def test_choices_validation_supports_named_groups(self):
        f = models.IntegerField(choices=(('group', ((10, 'A'), (20, 'B'))), (30, 'C')))
        self.assertEqual(10, f.clean(10, None))

    def test_nullable_integerfield_raises_error_with_blank_false(self):
        f = models.IntegerField(null=True, blank=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)

    def test_nullable_integerfield_cleans_none_on_null_and_blank_true(self):
        f = models.IntegerField(null=True, blank=True)
        self.assertIsNone(f.clean(None, None))

    def test_integerfield_raises_error_on_empty_input(self):
        f = models.IntegerField(null=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)
        with self.assertRaises(ValidationError):
            f.clean('', None)

    def test_integerfield_validates_zero_against_choices(self):
        """
        Test the validation of an IntegerField with choices that does not include zero.
        
        This function tests whether an IntegerField, configured with choices that exclude zero, raises a ValidationError when zero is passed as input.
        
        Parameters:
        f (IntegerField): The IntegerField instance with choices set to ((1, 1),).
        
        Returns:
        None: The function asserts that a ValidationError is raised when '0' is passed to the clean method of the field. No value is passed as the second argument to the clean
        """

        f = models.IntegerField(choices=((1, 1),))
        with self.assertRaises(ValidationError):
            f.clean('0', None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.IntegerField(choices=self.Choices.choices)
        self.assertEqual(f.clean('1', None), 1)

    def test_enum_choices_invalid_input(self):
        f = models.IntegerField(choices=self.Choices.choices)
        with self.assertRaises(ValidationError):
            f.clean('A', None)
        with self.assertRaises(ValidationError):
            f.clean('3', None)
