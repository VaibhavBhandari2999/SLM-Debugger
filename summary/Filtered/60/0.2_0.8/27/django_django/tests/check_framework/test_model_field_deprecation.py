from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('check_framework')
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        class MyField(models.Field):
            system_check_deprecated_details = {}

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(model.check(), [
            checks.Warning(
                msg='MyField has been deprecated.',
                obj=Model._meta.get_field('name'),
                id='fields.WXXX',
            )
        ])

    def test_user_specified_details(self):
        class MyField(models.Field):
            system_check_deprecated_details = {
                'msg': 'This field is deprecated and will be removed soon.',
                'hint': 'Use something else.',
                'id': 'fields.W999',
            }

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(model.check(), [
            checks.Warning(
                msg='This field is deprecated and will be removed soon.',
                hint='Use something else.',
                obj=Model._meta.get_field('name'),
                id='fields.W999',
            )
        ])


@isolate_apps('check_framework')
class TestRemovedField(SimpleTestCase):
    def test_default_details(self):
        class MyField(models.Field):
            system_check_removed_details = {}

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(model.check(), [
            checks.Error(
                msg='MyField has been removed except for support in historical migrations.',
                obj=Model._meta.get_field('name'),
                id='fields.EXXX',
            )
        ])

    def test_user_specified_details(self):
        """
        Tests the user-specified details for a custom field in a Django model.
        
        This function checks if the custom field `MyField` has the correct system check removed details specified. It creates a Django model with a field of type `MyField` and checks the result of the model's `check` method.
        
        Parameters:
        None
        
        Returns:
        list: A list of check results, expected to contain a single `Error` object with specific message, hint, object, and id.
        
        Key Details
        """

        class MyField(models.Field):
            system_check_removed_details = {
                'msg': 'Support for this field is gone.',
                'hint': 'Use something else.',
                'id': 'fields.E999',
            }

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(model.check(), [
            checks.Error(
                msg='Support for this field is gone.',
                hint='Use something else.',
                obj=Model._meta.get_field('name'),
                id='fields.E999',
            )
        ])
lds.E999',
            )
        ])
