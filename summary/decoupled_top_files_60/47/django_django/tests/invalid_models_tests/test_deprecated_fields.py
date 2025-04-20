from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the behavior of the deprecated IPAddressField in Django models.
        
        This function creates a model with an IPAddressField and checks if the field is flagged as deprecated. It expects to receive a list of checks, with a single error indicating that the IPAddressField has been removed and should be replaced with GenericIPAddressField.
        
        Parameters:
        - None
        
        Returns:
        - A list of Django checks, expected to contain a single Error object indicating that the IPAddressField is deprecated and should be replaced with GenericIPAddressField.
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
        """
        Tests the deprecation warning for the NullBooleanField.
        
        This function checks the deprecation warning for the NullBooleanField in Django models. It creates a model with a NullBooleanField and verifies that a warning is raised indicating that NullBooleanField is deprecated and should be replaced with BooleanField(null=True).
        
        Parameters:
        None
        
        Returns:
        list: A list of checks, where each check is a dictionary-like object containing the warning message, hint, and other details about the deprecation.
        
        Key Points
        """

        class NullBooleanFieldModel(models.Model):
            nb = models.NullBooleanField()

        model = NullBooleanFieldModel()
        self.assertEqual(model.check(), [
            checks.Warning(
                'NullBooleanField is deprecated. Support for it (except in '
                'historical migrations) will be removed in Django 4.0.',
                hint='Use BooleanField(null=True) instead.',
                obj=NullBooleanFieldModel._meta.get_field('nb'),
                id='fields.W903',
            ),
        ])
