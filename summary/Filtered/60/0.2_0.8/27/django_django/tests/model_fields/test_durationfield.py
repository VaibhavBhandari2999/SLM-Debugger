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
        Test the roundtrip functionality for storing and retrieving a datetime.timedelta object in a database.
        
        This test creates a DurationModel instance with a specified timedelta object and then retrieves it to ensure that the stored value matches the original.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A timedelta object with microseconds is created and saved.
        - The object is retrieved from the database.
        - The retrieved timedelta is compared to the original to ensure correctness.
        """

        duration = datetime.timedelta(microseconds=8999999999999999)
        DurationModel.objects.create(field=duration)
        loaded = DurationModel.objects.get()
        self.assertEqual(loaded.field, duration)

    def test_create_empty(self):
        NullDurationModel.objects.create()
        loaded = NullDurationModel.objects.get()
        self.assertIsNone(loaded.field)

    def test_fractional_seconds(self):
        """
        Test the handling of fractional seconds in a DurationModel.
        
        This function creates a DurationModel instance with a timedelta object containing fractional seconds and checks if the value is correctly stored and retrieved.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - value: A datetime.timedelta object with a fractional second value of 2.05 seconds.
        
        Steps:
        1. Create a DurationModel instance with the given timedelta value.
        2. Refresh the model instance from the database.
        3. Assert that the
        """

        value = datetime.timedelta(seconds=2.05)
        d = DurationModel.objects.create(field=value)
        d.refresh_from_db()
        self.assertEqual(d.field, value)


class TestQuerying(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.objs = [
            DurationModel.objects.create(field=datetime.timedelta(days=1)),
            DurationModel.objects.create(field=datetime.timedelta(seconds=1)),
            DurationModel.objects.create(field=datetime.timedelta(seconds=-1)),
        ]

    def test_exact(self):
        self.assertSequenceEqual(
            DurationModel.objects.filter(field=datetime.timedelta(days=1)),
            [self.objs[0]]
        )

    def test_gt(self):
        self.assertSequenceEqual(
            DurationModel.objects.filter(field__gt=datetime.timedelta(days=0)),
            [self.objs[0], self.objs[1]]
        )


class TestSerialization(SimpleTestCase):
    test_data = '[{"fields": {"field": "1 01:00:00"}, "model": "model_fields.durationmodel", "pk": null}]'

    def test_dumping(self):
        instance = DurationModel(field=datetime.timedelta(days=1, hours=1))
        data = serializers.serialize('json', [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize('json', self.test_data))[0].object
        self.assertEqual(instance.field, datetime.timedelta(days=1, hours=1))


class TestValidation(SimpleTestCase):

    def test_invalid_string(self):
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
rmfield(), forms.DurationField)
