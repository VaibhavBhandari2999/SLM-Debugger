from unittest import skipUnless

from django.core import checks
from django.db import connection, models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField.
        
        This function checks the deprecation of the IPAddressField in Django models. It creates a model with an IPAddressField and verifies that a deprecation warning is raised. The warning indicates that the IPAddressField has been removed except for support in historical migrations, and suggests using GenericIPAddressField instead.
        
        Parameters:
        None
        
        Returns:
        list: A list of check results, which in this case contains a single Error object indicating the deprecation of IPAddressField and suggesting the
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
        Tests the deprecation warning for the `JSONField` in `django.contrib.postgres.fields`.
        
        This function checks the deprecation warning for the `JSONField` in `django.contrib.postgres.fields`. It creates a model with a `JSONField` and verifies that the warning is raised.
        
        Parameters:
        - None
        
        Returns:
        - A list of `checks.Error` objects indicating the deprecation warning for the `JSONField`.
        
        Key Points:
        - The function uses the `JSONField` from `django
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
