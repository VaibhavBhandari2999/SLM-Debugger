from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField in Django models.
        
        This function checks if the use of IPAddressField in a Django model is deprecated. It creates a model with an IPAddressField and checks for deprecation warnings. The expected output is a list of checks, where the first element is an error indicating that IPAddressField has been removed and should be replaced with GenericIPAddressField.
        
        Parameters:
        - None
        
        Returns:
        - list: A list of checks, where the first element is an error message indicating the de
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
        
        This function checks the deprecation warning for the NullBooleanField in Django models. It creates a model with a NullBooleanField and expects a warning to be raised indicating that NullBooleanField is deprecated and should be replaced with BooleanField(null=True). The warning is expected to be a warning of type 'fields.W903'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        checks.Warning: If the check does not raise the
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
