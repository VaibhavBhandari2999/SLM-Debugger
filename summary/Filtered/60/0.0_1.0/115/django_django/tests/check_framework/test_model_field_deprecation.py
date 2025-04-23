from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("check_framework")
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details for a deprecated field in a Django model.
        
        This function creates a custom Django model field `MyField` that does not specify any deprecated details. It then defines a model `Model` with a field `name` of type `MyField`. The function checks the model for deprecation warnings and asserts that the check returns a single warning message indicating that `MyField` has been deprecated, with the warning's message, object, and unique identifier.
        
        Parameters:
        None
        
        Returns
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
        Tests the user-specified details for a custom field in a Django model.
        
        This function checks if the custom field `MyField` correctly sets the deprecated details when used in a Django model. The function creates an instance of the model and checks if the field's deprecation warning is generated as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - `MyField`: A custom Django model field that specifies deprecation details.
        - `Model`: A Django model containing an instance of
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
        Tests the default details for a custom field that has been removed.
        
        This function checks the behavior of a custom Django model field, `MyField`, which has been deprecated and removed except for support in historical migrations. The test ensures that when an instance of the model is checked, it raises an error indicating that the field has been removed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `MyField` class is defined as a subclass of `models.Field` and has an
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
        Tests the user-specified details for a custom field in a Django model.
        
        This function checks the custom field `MyField` in the `Model` class to ensure that the system check details are correctly specified. The `MyField` class overrides the `system_check_removed_details` attribute to provide a specific error message, hint, and unique check ID. The function creates an instance of the `Model` and checks its fields using Django's model validation. The expected output is a list containing a single
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
