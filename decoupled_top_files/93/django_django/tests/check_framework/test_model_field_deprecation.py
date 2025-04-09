"""
The provided Python file contains unit tests for custom Django fields using the `Django` framework. Specifically, it focuses on testing the behavior of fields when they are marked as deprecated or removed. The file defines two test classes, `TestDeprecatedField` and `TestRemovedField`, each containing methods to test different scenarios related to deprecated and removed fields. These tests ensure that the custom fields raise appropriate warnings or errors when used in a Django model, depending on their status. The tests cover both default and user-specified details for these checks, verifying that the correct messages, hints, objects, and IDs are returned by the `check()` method of the model. The tests are isolated to the "check_framework" app to avoid conflicts with other apps during
"""
from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("check_framework")
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details of a custom field in a Django model.
        
        This function creates an instance of a Django model with a custom field
        `MyField` that has no deprecated details defined. It then checks the model
        for deprecation warnings and asserts that the warning message is as
        expected.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the check result does not match the expected warning.
        
        Important Functions:
        - `test
        """

        class MyField(models.Field):
            system_check_deprecated_details = {}

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(
            model.check(),
            [
                checks.Warning(
                    msg="MyField has been deprecated.",
                    obj=Model._meta.get_field("name"),
                    id="fields.WXXX",
                )
            ],
        )

    def test_user_specified_details(self):
        """
        Tests that user-specified details for a deprecated field are correctly identified and returned.
        
        This function checks if the `system_check_deprecated_details` attribute of a custom field (`MyField`) is properly set and if the `check()` method of a model (`Model`) returns the expected warning message, hint, object, and check ID.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `models.Field`: Custom field class with deprecated details.
        - `
        """

        class MyField(models.Field):
            system_check_deprecated_details = {
                "msg": "This field is deprecated and will be removed soon.",
                "hint": "Use something else.",
                "id": "fields.W999",
            }

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(
            model.check(),
            [
                checks.Warning(
                    msg="This field is deprecated and will be removed soon.",
                    hint="Use something else.",
                    obj=Model._meta.get_field("name"),
                    id="fields.W999",
                )
            ],
        )


@isolate_apps("check_framework")
class TestRemovedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details for a custom field that has been removed, ensuring that the check raises an error with the expected message and identifier.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        Error: An error check is raised if the custom field `MyField` is used in the model.
        
        Important Functions:
        - `test_default_details`: The main function being tested.
        - `MyField`: A custom field class derived from `models.Field`.
        - `
        """

        class MyField(models.Field):
            system_check_removed_details = {}

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(
            model.check(),
            [
                checks.Error(
                    msg=(
                        "MyField has been removed except for support in historical "
                        "migrations."
                    ),
                    obj=Model._meta.get_field("name"),
                    id="fields.EXXX",
                )
            ],
        )

    def test_user_specified_details(self):
        """
        Tests user-specified details for a custom field in a Django model.
        
        This function checks if the specified field in a Django model raises an error
        with the given system check removed details. The custom field `MyField` is defined
        with specific system check removed details, and the model `Model` contains an instance
        of this field named `name`. The function asserts that the check method on the model
        returns an error with the expected message, hint, object, and
        """

        class MyField(models.Field):
            system_check_removed_details = {
                "msg": "Support for this field is gone.",
                "hint": "Use something else.",
                "id": "fields.E999",
            }

        class Model(models.Model):
            name = MyField()

        model = Model()
        self.assertEqual(
            model.check(),
            [
                checks.Error(
                    msg="Support for this field is gone.",
                    hint="Use something else.",
                    obj=Model._meta.get_field("name"),
                    id="fields.E999",
                )
            ],
        )
