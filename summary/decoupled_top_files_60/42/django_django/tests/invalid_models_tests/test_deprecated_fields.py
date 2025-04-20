from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField.
        
        This function checks if the usage of IPAddressField in a model is deprecated and should be replaced with GenericIPAddressField. It creates an instance of a model with an IPAddressField and checks the validation result.
        
        Parameters:
        None
        
        Returns:
        list: A list of validation errors, where each error is an instance of checks.Error. The error indicates that IPAddressField has been removed and should be replaced with GenericIPAddressField.
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
        Tests the deprecation warning for NullBooleanField.
        
        This function checks the deprecation warning for the NullBooleanField in a Django model.
        It creates a model with a NullBooleanField and asserts that the check method returns a warning.
        The warning indicates that NullBooleanField is deprecated and will be removed in Django 4.0.
        The warning also suggests using BooleanField(null=True) as an alternative.
        
        Parameters:
        None
        
        Returns:
        None
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
