from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('check_framework')
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details for a deprecated field in a Django model.
        
        This function creates a custom Django model field `MyField` with an empty `system_check_deprecated_details` dictionary. It then defines a Django model `Model` with a field `name` of type `MyField`. The function checks the model for deprecation warnings and asserts that the check returns a single warning message indicating that `MyField` has been deprecated. The warning message includes the field name and the unique identifier for the
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
        """
        Test the default details for a custom field that has been deprecated.
        
        This function checks the behavior of a custom field `MyField` that has been removed except for support in historical migrations. It creates a model with an instance of `MyField` and verifies that the field triggers a specific error check during model validation.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The function uses a custom field `MyField` with an empty `system_check_removed_details` dictionary.
        - A
        """

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
