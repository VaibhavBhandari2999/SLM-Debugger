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
        Test the round-trip functionality for storing and retrieving a datetime.timedelta object.
        
        This test checks if a timedelta object can be correctly saved to the database and then retrieved without any loss of precision.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A timedelta object with a very large number of microseconds (8999999999999999) is created.
        - The timedelta object is saved to a database model instance.
        - The
        """

        duration = datetime.timedelta(microseconds=8999999999999999)
        DurationModel.objects.create(field=duration)
        loaded = DurationModel.objects.get()
        self.assertEqual(loaded.field, duration)

    def test_create_empty(self):
        """
        Test the creation of an empty instance of NullDurationModel.
        
        This function creates an instance of NullDurationModel with no specified values and checks if the 'field' attribute of the loaded instance is None.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        - No specific keywords are used in this function.
        
        Input:
        - No external input is required for this function.
        
        Output:
        - The function asserts that the 'field' attribute of the loaded instance is None.
        """

        NullDurationModel.objects.create()
        loaded = NullDurationModel.objects.get()
        self.assertIsNone(loaded.field)

    def test_fractional_seconds(self):
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
            [self.objs[0]],
        )

    def test_gt(self):
        self.assertCountEqual(
            DurationModel.objects.filter(field__gt=datetime.timedelta(days=0)),
            [self.objs[0], self.objs[1]],
        )


class TestSerialization(SimpleTestCase):
    test_data = (
        '[{"fields": {"field": "1 01:00:00"}, "model": "model_fields.durationmodel", '
        '"pk": null}]'
    )

    def test_dumping(self):
        instance = DurationModel(field=datetime.timedelta(days=1, hours=1))
        data = serializers.serialize("json", [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize("json", self.test_data))[0].object
        self.assertEqual(instance.field, datetime.timedelta(days=1, hours=1))


class TestValidation(SimpleTestCase):
    def test_invalid_string(self):
        """
        Tests the validation of an invalid string input for a DurationField.
        
        This function tests the behavior of the `clean` method of a DurationField when an invalid string is provided. It raises a ValidationError with a specific error code and message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string is not in the correct format for a duration (e.g., "not a datetime").
        
        Example:
        >>> test_invalid_string()
        ValidationError raised with code 'invalid'
        """

        field = models.DurationField()
        with self.assertRaises(exceptions.ValidationError) as cm:
            field.clean("not a datetime", None)
        self.assertEqual(cm.exception.code, "invalid")
        self.assertEqual(
            cm.exception.message % cm.exception.params,
            "“not a datetime” value has an invalid format. "
            "It must be in [DD] [[HH:]MM:]ss[.uuuuuu] format.",
        )


class TestFormField(SimpleTestCase):
    # Tests for forms.DurationField are in the forms_tests app.

    def test_formfield(self):
        field = models.DurationField()
        self.assertIsInstance(field.formfield(), forms.DurationField)
