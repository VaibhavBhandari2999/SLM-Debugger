from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('check_framework')
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details for a deprecated field in a Django model.
        
        This function checks the behavior of a custom Django model field that has been marked as deprecated. It creates a custom field `MyField` with an empty `system_check_deprecated_details` dictionary, and a model `Model` that uses this field. The function then checks the model instance for deprecation warnings and asserts that the warning is correctly generated with the expected message, object, and check ID.
        
        Key Parameters:
        - None
        
        Input
        """

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
        
        This function checks if the custom field `MyField` correctly sets the deprecated details when creating a model with it. The function creates an instance of the model and checks if the field's deprecation warning is correctly generated and formatted.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - A custom field `MyField` is defined with specific deprecation details.
        - A model `Model` is created using this custom field.
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
      ])
