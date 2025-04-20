from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField in Django models.
        
        This function checks if the use of IPAddressField in a Django model is deprecated. It creates a model with an IPAddressField and checks for any validation errors. The expected error is that the IPAddressField has been removed and should be replaced with GenericIPAddressField. The function returns a list of checks, which in this case should contain a single error message indicating the deprecation and suggesting a replacement.
        
        Parameters:
        - None
        
        Returns:
        - A list of
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
        """
        Tests the deprecation of CommaSeparatedIntegerField.
        
        This function checks if the CommaSeparatedIntegerField is deprecated and returns an error if it is used. The model CommaSeparatedIntegerModel is created with a CommaSeparatedIntegerField field. The check method is called on the model to validate the field. The expected output is a list containing a single error, indicating that CommaSeparatedIntegerField is removed except for support in historical migrations. The hint suggests using CharField with a validator instead.
        """

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
            checks.Warning(
                'NullBooleanField is deprecated. Support for it (except in '
                'historical migrations) will be removed in Django 4.0.',
                hint='Use BooleanField(null=True) instead.',
                obj=NullBooleanFieldModel._meta.get_field('nb'),
                id='fields.W903',
            ),
        ])
