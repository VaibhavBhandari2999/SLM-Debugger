import unittest

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, models
from django.test import SimpleTestCase, TestCase

from .models import (
    BigIntegerModel, IntegerModel, PositiveIntegerModel,
    PositiveSmallIntegerModel, SmallIntegerModel,
)


class IntegerFieldTests(TestCase):
    model = IntegerModel
    documented_range = (-2147483648, 2147483647)

    @property
    def backend_range(self):
        """
        Generates the range of values for a backend-specific integer field.
        
        This method retrieves the range of values for an integer field on the model.
        It uses the field's internal type to query the database backend for the valid range of values.
        
        Parameters:
        None
        
        Returns:
        A tuple representing the minimum and maximum values for the integer field.
        The returned tuple will be in the form (min_value, max_value).
        
        Note:
        The function relies on the database connection and the model's field configuration
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
        
        This function creates an instance of the model with an integer value, checks the type, saves the instance, and checks the type again. It also retrieves the instance from the database and checks the type of the 'value' attribute.
        
        Parameters:
        None
        
        Returns:
        None
        """

        instance = self.model(value=1)
        self.assertIsInstance(instance.value, int)
        instance.save()
        self.assertIsInstance(instance.value, int)
        instance = self.model.objects.get()
        self.assertIsInstance(instance.value, int)

    def test_coercing(self):
        """
        Tests the coercion of string values to integers in the model's value field.
        
        This function creates an instance of the model with a string value '10' and retrieves it. It then checks if the value has been coerced to an integer 10.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - instance: The model instance retrieved from the database.
        - value: The coerced integer value of the model instance's field.
        """

        self.model.objects.create(value='10')
        instance = self.model.objects.get(value='10')
        self.assertEqual(instance.value, 10)

    def test_invalid_value(self):
        """
        Tests the validation of invalid input values for the 'value' field in the model.
        
        This function tests various types of invalid input values for the 'value' field in the model. It expects the field to raise specific exceptions with appropriate error messages for each type of invalid input.
        
        Parameters:
        - exception (type): The expected exception type to be raised.
        - value (varies): The invalid input value to be tested.
        
        Returns:
        - None: The function asserts that the correct exception is raised with the
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
        Test the behavior of the PositiveIntegerModel when attempting to set a value to a negative number.
        
        This test creates an instance of PositiveIntegerModel with an initial value of 0. It then attempts to decrement the value by 1 using F-expression. The test expects an IntegrityError to be raised, indicating that the model's constraints prevent the value from going below zero.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        IntegrityError: If the value is successfully set to a negative number
        """

        p = PositiveIntegerModel.objects.create(value=0)
        p.value = models.F('value') - 1
        with self.assertRaises(IntegrityError):
            p.save()


class ValidationTests(SimpleTestCase):

    class Choices(models.IntegerChoices):
        A = 1

    def test_integerfield_cleans_valid_string(self):
        f = models.IntegerField()
        self.assertEqual(f.clean('2', None), 2)

    def test_integerfield_raises_error_on_invalid_intput(self):
        """
        Tests that an IntegerField raises a ValidationError when an invalid input is provided.
        
        This function creates an IntegerField instance and attempts to clean an invalid input ('a').
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input is not a valid integer.
        
        Key Points:
        - The function uses a context manager to assert that a ValidationError is raised.
        - The input 'a' is not a valid integer, hence the expected behavior is to raise a ValidationError.
        """

        f = models.IntegerField()
        with self.assertRaises(ValidationError):
            f.clean('a', None)

    def test_choices_validation_supports_named_groups(self):
        f = models.IntegerField(choices=(('group', ((10, 'A'), (20, 'B'))), (30, 'C')))
        self.assertEqual(10, f.clean(10, None))

    def test_nullable_integerfield_raises_error_with_blank_false(self):
        """
        Tests that a ValidationError is raised when attempting to clean a null value for an IntegerField with null=True and blank=False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the clean method does not raise a ValidationError when None is passed as input.
        
        Key Points:
        - The function creates an IntegerField instance with null=True and blank=False.
        - It then attempts to clean None using the clean method of the field.
        - The test asserts that a ValidationError is raised during this process
        """

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
ne)
