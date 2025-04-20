from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("check_framework")
class TestDeprecatedField(SimpleTestCase):
    def test_default_details(self):
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
        """
        Tests the default details for a custom field that has been removed.
        
        This function checks the behavior of a custom Django model field that has been deprecated. The field, `MyField`, is defined without any custom system check removed details. When a model, `Model`, uses this field, the function asserts that the field's checks return a specific error message indicating that the field has been removed except for support in historical migrations.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The check
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
        
        This function checks if the custom field `MyField` in the `Model` class raises an error with the specified system check details. The `MyField` class has a `system_check_removed_details` attribute that defines the error message, hint, and check ID. The `Model` class contains a field `name` of type `MyField`. The function creates an instance of `Model` and checks the result of
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
