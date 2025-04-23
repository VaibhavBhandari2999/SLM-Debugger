from unittest import skipUnless

from django.core import checks
from django.db import connection, models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField in Django models.
        
        This function checks if the use of IPAddressField in a Django model is deprecated. It creates a model with an IPAddressField and checks if the model's validation returns an error indicating that IPAddressField has been removed and should be replaced with GenericIPAddressField.
        
        Parameters:
        - None
        
        Returns:
        - list: A list of validation checks, where each check is an instance of Django's checks framework. The list will contain an error if IPAddressField is used
        """

        class IPAddressModel(models.Model):
            ip = models.IPAddressField()

        model = IPAddressModel()
        self.assertEqual(
            model.check(),
            [checks.Error(
                'IPAddressField has been removed except for support in '
                'historical migrations.',
                hint='Use GenericIPAddressField instead.',
                obj=IPAddressModel._meta.get_field('ip'),
                id='fields.E900',
            )],
        )

    def test_CommaSeparatedIntegerField_deprecated(self):
        class CommaSeparatedIntegerModel(models.Model):
            csi = models.CommaSeparatedIntegerField(max_length=64)

        model = CommaSeparatedIntegerModel()
        self.assertEqual(
            model.check(),
            [checks.Error(
                'CommaSeparatedIntegerField is removed except for support in '
                'historical migrations.',
                hint='Use CharField(validators=[validate_comma_separated_integer_list]) instead.',
                obj=CommaSeparatedIntegerModel._meta.get_field('csi'),
                id='fields.E901',
            )],
        )

    def test_nullbooleanfield_deprecated(self):
        class NullBooleanFieldModel(models.Model):
            nb = models.NullBooleanField()

        model = NullBooleanFieldModel()
        self.assertEqual(model.check(), [
            checks.Error(
                'NullBooleanField is removed except for support in historical '
                'migrations.',
                hint='Use BooleanField(null=True) instead.',
                obj=NullBooleanFieldModel._meta.get_field('nb'),
                id='fields.E903',
            ),
        ])

    @skipUnless(connection.vendor == 'postgresql', 'PostgreSQL specific SQL')
    def test_postgres_jsonfield_deprecated(self):
        """
        Tests the deprecation of the JSONField in Django's postgres module.
        
        This function checks for the deprecation warning of the JSONField in the
        django.contrib.postgres.fields module. It creates a model with a JSONField
        and checks for the expected error message indicating that the field is
        deprecated and should be replaced with django.db.models.JSONField.
        
        Parameters:
        None
        
        Returns:
        list: A list of check messages, expected to contain a single Error
        message indicating the deprecation of
        """

        from django.contrib.postgres.fields import JSONField

        class PostgresJSONFieldModel(models.Model):
            field = JSONField()

        self.assertEqual(PostgresJSONFieldModel.check(), [
            checks.Error(
                'django.contrib.postgres.fields.JSONField is removed except '
                'for support in historical migrations.',
                hint='Use django.db.models.JSONField instead.',
                obj=PostgresJSONFieldModel._meta.get_field('field'),
                id='fields.E904',
            ),
        ])
