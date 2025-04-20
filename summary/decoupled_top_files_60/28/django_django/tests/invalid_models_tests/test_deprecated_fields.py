from django.core import checks
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps


@isolate_apps('invalid_models_tests')
class DeprecatedFieldsTests(SimpleTestCase):
    def test_IPAddressField_deprecated(self):
        """
        Tests the deprecation of IPAddressField.
        
        This function checks if the usage of IPAddressField in a model is deprecated and should be replaced with GenericIPAddressField. It creates an instance of a model with an IPAddressField and verifies that the check method returns an error indicating the deprecation of IPAddressField and suggesting the use of GenericIPAddressField instead.
        
        Parameters:
        None
        
        Returns:
        list: A list of check results, expected to contain a single Error check indicating the deprecation of IPAddressField and suggesting
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
        Test the deprecation of CommaSeparatedIntegerField.
        
        This function checks if the CommaSeparatedIntegerField is marked as deprecated and if it suggests an alternative field type.
        
        Parameters:
        None
        
        Returns:
        list: A list of check results, specifically an error indicating that CommaSeparatedIntegerField is removed except for support in historical migrations, and suggesting to use CharField with a specific validator instead.
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
