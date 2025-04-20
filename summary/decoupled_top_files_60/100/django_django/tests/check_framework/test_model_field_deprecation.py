from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("check_framework")
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
        """
        Tests the default details for a deprecated field in a Django model.
        
        This function checks the behavior of a custom Django model field that has been deprecated. It creates a model with a field of type `MyField`, which is a subclass of `models.Field` with an empty `system_check_deprecated_details` dictionary. The function then performs a check on an instance of the model and asserts that the check returns a warning indicating that the field has been deprecated.
        
        Key Parameters:
        - None
        
        Input:
        -
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
        Tests the user-specified details for a custom model field.
        
        This function checks the custom model field `MyField` to ensure that the system check details are correctly specified. It creates a model with a field of type `MyField` and performs a check on the model to verify that the expected error message, hint, and check ID are returned.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Details:
        - `MyField`: A custom model field class with specified system check details.
        -
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
