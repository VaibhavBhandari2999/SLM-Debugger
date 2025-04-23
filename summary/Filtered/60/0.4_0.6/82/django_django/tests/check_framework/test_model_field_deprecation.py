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
        """
        Tests the user-specified details for a custom model field.
        
        This function checks if the custom field `MyField` correctly sets the deprecated details when creating a model with it. The function creates an instance of the model and checks the result of the model's `check` method.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A custom field `MyField` is defined with specific deprecated details.
        - A model `Model` is created using this custom field.
        - The `
        """

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
        
        This function checks if the custom field `MyField` correctly specifies the details for system check removal. The field is expected to have a specific message, hint, and unique identifier for the check.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - A custom field `MyField` is defined with specific system check details.
        - A model `Model` is created with an instance of `MyField
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
