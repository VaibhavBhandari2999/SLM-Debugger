import datetime
import json

from django import forms
from django.core import exceptions, serializers
from django.db import models
from django.test import SimpleTestCase, TestCase

from .models import DurationModel, NullDurationModel


class TestSaveLoad(TestCase):

    def test_simple_roundtrip(self):
        """
        Tests the round-trip functionality of saving and loading a `datetime.timedelta` object using the `DurationModel`. Creates a `DurationModel` instance with a specified `timedelta` value, saves it to the database, retrieves it, and verifies that the original `timedelta` is preserved upon re-loading.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `datetime.timedelta`
        - `DurationModel.objects.create()`
        - `DurationModel.objects.get
        """

        duration = datetime.timedelta(microseconds=8999999999999999)
        DurationModel.objects.create(field=duration)
        loaded = DurationModel.objects.get()
        self.assertEqual(loaded.field, duration)

    def test_create_empty(self):
        """
        Create an empty instance of NullDurationModel and verify that the 'field' is None.
        
        This test creates an empty instance of the NullDurationModel using `objects.create()`, retrieves the created instance using `objects.get()`, and asserts that the 'field' attribute is None using `self.assertIsNone()`.
        
        Functions Used:
        - `NullDurationModel.objects.create()`: Creates an empty instance of NullDurationModel.
        - `NullDurationModel.objects.get()`: Retrieves the created instance
        """

        NullDurationModel.objects.create()
        loaded = NullDurationModel.objects.get()
        self.assertIsNone(loaded.field)

    def test_fractional_seconds(self):
        """
        Tests the handling of fractional seconds in a DurationModel field.
        
        This function creates a `DurationModel` instance with a `timedelta` object
        containing fractional seconds (2.05 seconds). It then retrieves the model
        from the database and checks if the stored value matches the original value.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `datetime.timedelta`: Used to create a `timedelta` object with fractional seconds.
        - `
        """

        value = datetime.timedelta(seconds=2.05)
        d = DurationModel.objects.create(field=value)
        d.refresh_from_db()
        self.assertEqual(d.field, value)


class TestQuerying(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the DurationModel class.
        
        This method creates three instances of the DurationModel with different timedelta values and stores them in the `cls.objs` list.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DurationModel.objects.create()`: Creates new instances of the DurationModel with specified `field` values.
        - `datetime.timedelta()`: Represents durations in terms of days, seconds, etc.
        
        Input Variables:
        None
        """

        cls.objs = [
            DurationModel.objects.create(field=datetime.timedelta(days=1)),
            DurationModel.objects.create(field=datetime.timedelta(seconds=1)),
            DurationModel.objects.create(field=datetime.timedelta(seconds=-1)),
        ]

    def test_exact(self):
        """
        Tests if the `DurationModel` objects with a specific `field` value equal to one day (24 hours) are correctly filtered and returned.
        
        Summary:
        - Function: `test_exact`
        - Input: None
        - Output: A list of `DurationModel` objects where the `field` is exactly one day (24 hours).
        - Key Functions: `assertSequenceEqual`, `filter`, `datetime.timedelta`
        """

        self.assertSequenceEqual(
            DurationModel.objects.filter(field=datetime.timedelta(days=1)),
            [self.objs[0]]
        )

    def test_gt(self):
        """
        Tests the filtering of `DurationModel` objects where the `field` is greater than a zero-day `datetime.timedelta`.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `assertSequenceEqual`: Compares the filtered queryset with the expected list of objects.
        - `filter`: Filters the `DurationModel` objects based on the condition that `field` is greater than `datetime.timedelta(days=0)`.
        
        Important Variables:
        - `self.objs
        """

        self.assertSequenceEqual(
            DurationModel.objects.filter(field__gt=datetime.timedelta(days=0)),
            [self.objs[0], self.objs[1]]
        )


class TestSerialization(SimpleTestCase):
    test_data = '[{"fields": {"field": "1 01:00:00"}, "model": "model_fields.durationmodel", "pk": null}]'

    def test_dumping(self):
        """
        Tests the serialization of a DurationModel instance using JSON format.
        
        This function creates an instance of DurationModel with a specific datetime.timedelta value, serializes it into JSON format using the `serializers.serialize` function, and then compares the serialized data with a predefined test data using the `json.loads` function.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DurationModel`: The model being tested.
        - `datetime.timedelta`: The time delta value used
        """

        instance = DurationModel(field=datetime.timedelta(days=1, hours=1))
        data = serializers.serialize('json', [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize('json', self.test_data))[0].object
        self.assertEqual(instance.field, datetime.timedelta(days=1, hours=1))


class TestValidation(SimpleTestCase):

    def test_invalid_string(self):
        """
        Tests that a ValidationError is raised when attempting to clean an invalid string for a DurationField.
        
        Args:
        self: The instance of the test case.
        
        Raises:
        ValidationError: If the input string is not in a valid duration format.
        
        Summary:
        This function tests the validation of a DurationField by passing an invalid string and expecting a ValidationError. It uses the `clean` method of the DurationField to validate the input and checks if the exception raised matches the expected error code and message
        """

        field = models.DurationField()
        with self.assertRaises(exceptions.ValidationError) as cm:
            field.clean('not a datetime', None)
        self.assertEqual(cm.exception.code, 'invalid')
        self.assertEqual(
            cm.exception.message % cm.exception.params,
            '“not a datetime” value has an invalid format. '
            'It must be in [DD] [[HH:]MM:]ss[.uuuuuu] format.'
        )


class TestFormField(SimpleTestCase):
    # Tests for forms.DurationField are in the forms_tests app.

    def test_formfield(self):
        field = models.DurationField()
        self.assertIsInstance(field.formfield(), forms.DurationField)
