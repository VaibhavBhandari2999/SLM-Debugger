from unittest import skipUnless

from django.core import checks
from django.db import connection, models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps("invalid_models_tests")
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        class IPAddressModel(models.Model):
            ip = models.IPAddressField()

        model = IPAddressModel()
        self.assertEqual(
            model.check(),
            [
                checks.Error(
                    "IPAddressField has been removed except for support in "
                    "historical migrations.",
                    hint="Use GenericIPAddressField instead.",
                    obj=IPAddressModel._meta.get_field("ip"),
                    id="fields.E900",
                )
            ],
        )

    def test_CommaSeparatedIntegerField_deprecated(self):
        """
        Tests the deprecation of CommaSeparatedIntegerField.
        
        This function checks the deprecation of the CommaSeparatedIntegerField in Django models.
        It creates a model with a CommaSeparatedIntegerField and verifies that a deprecation warning is raised.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        Error: If the deprecation warning is not correctly raised.
        """

        class CommaSeparatedIntegerModel(models.Model):
            csi = models.CommaSeparatedIntegerField(max_length=64)

        model = CommaSeparatedIntegerModel()
        self.assertEqual(
            model.check(),
            [
                checks.Error(
                    "CommaSeparatedIntegerField is removed except for support in "
                    "historical migrations.",
                    hint=(
                        "Use "
                        "CharField(validators=[validate_comma_separated_integer_list]) "
                        "instead."
                    ),
                    obj=CommaSeparatedIntegerModel._meta.get_field("csi"),
                    id="fields.E901",
                )
            ],
        )

    def test_nullbooleanfield_deprecated(self):
        class NullBooleanFieldModel(models.Model):
            nb = models.NullBooleanField()

        model = NullBooleanFieldModel()
        self.assertEqual(
            model.check(),
            [
                checks.Error(
                    "NullBooleanField is removed except for support in historical "
                    "migrations.",
                    hint="Use BooleanField(null=True) instead.",
                    obj=NullBooleanFieldModel._meta.get_field("nb"),
                    id="fields.E903",
                ),
            ],
        )

    @skipUnless(connection.vendor == "postgresql", "PostgreSQL specific SQL")
    def test_postgres_jsonfield_deprecated(self):
        """
        Tests the deprecation of the JSONField from django.contrib.postgres.fields. The function creates a model with a JSONField and checks for a deprecation warning. The model is expected to use django.db.models.JSONField instead.
        
        Args:
        None
        
        Returns:
        A list of checks, where each check is an Error object indicating a deprecation warning for the usage of django.contrib.postgres.fields.JSONField. The warning suggests using django.db.models.JSONField instead.
        
        Raises:
        None
        """

        from django.contrib.postgres.fields import JSONField

        class PostgresJSONFieldModel(models.Model):
            field = JSONField()

        self.assertEqual(
            PostgresJSONFieldModel.check(),
            [
                checks.Error(
                    "django.contrib.postgres.fields.JSONField is removed except "
                    "for support in historical migrations.",
                    hint="Use django.db.models.JSONField instead.",
                    obj=PostgresJSONFieldModel._meta.get_field("field"),
                    id="fields.E904",
                ),
            ],
        )
