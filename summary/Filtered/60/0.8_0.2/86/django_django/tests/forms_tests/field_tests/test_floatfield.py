from django.core.exceptions import ValidationError
from django.forms import FloatField, NumberInput
from django.test import SimpleTestCase
from django.test.utils import ignore_warnings, override_settings
from django.utils import formats, translation
from django.utils.deprecation import RemovedInDjango50Warning

from . import FormFieldAssertionsMixin


class FloatFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_floatfield_1(self):
        """
        Tests the behavior of the FloatField in Django forms.
        
        This function tests the FloatField of Django forms with various inputs and edge cases. It checks the rendering of the widget, validation of required fields, conversion of string inputs to floats, and handling of invalid inputs.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - The function does not return a value but performs assertions to validate the behavior of the FloatField.
        
        Assertions:
        1. The widget renders correctly
        """

        f = FloatField()
        self.assertWidgetRendersTo(f, '<input step="any" type="number" name="f" id="id_f" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1.0, f.clean('1'))
        self.assertIsInstance(f.clean('1'), float)
        self.assertEqual(23.0, f.clean('23'))
        self.assertEqual(3.1400000000000001, f.clean('3.14'))
        self.assertEqual(3.1400000000000001, f.clean(3.14))
        self.assertEqual(42.0, f.clean(42))
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean('a')
        self.assertEqual(1.0, f.clean('1.0 '))
        self.assertEqual(1.0, f.clean(' 1.0'))
        self.assertEqual(1.0, f.clean(' 1.0 '))
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean('1.0a')
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean('Infinity')
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean('NaN')
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean('-Inf')

    def test_floatfield_2(self):
        f = FloatField(required=False)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
        self.assertEqual(1.0, f.clean('1'))
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_floatfield_3(self):
        f = FloatField(max_value=1.5, min_value=0.5)
        self.assertWidgetRendersTo(
            f,
            '<input step="any" name="f" min="0.5" max="1.5" type="number" id="id_f" required>',
        )
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is less than or equal to 1.5.'"):
            f.clean('1.6')
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is greater than or equal to 0.5.'"):
            f.clean('0.4')
        self.assertEqual(1.5, f.clean('1.5'))
        self.assertEqual(0.5, f.clean('0.5'))
        self.assertEqual(f.max_value, 1.5)
        self.assertEqual(f.min_value, 0.5)

    def test_floatfield_widget_attrs(self):
        f = FloatField(widget=NumberInput(attrs={'step': 0.01, 'max': 1.0, 'min': 0.0}))
        self.assertWidgetRendersTo(
            f,
            '<input step="0.01" name="f" min="0.0" max="1.0" type="number" id="id_f" required>',
        )

    def test_floatfield_localized(self):
        """
        A localized FloatField's widget renders to a text input without any
        number input specific attributes.
        """
        f = FloatField(localize=True)
        self.assertWidgetRendersTo(f, '<input id="id_f" name="f" type="text" required>')

    def test_floatfield_changed(self):
        f = FloatField()
        n = 4.35
        self.assertFalse(f.has_changed(n, '4.3500'))

        with translation.override('fr'):
            f = FloatField(localize=True)
            localized_n = formats.localize_input(n)  # -> '4,35' in French
            self.assertFalse(f.has_changed(n, localized_n))

    # RemovedInDjango50Warning: When the deprecation ends, remove
    # @ignore_warnings and USE_L10N=False. The test should remain because
    # format-related settings will take precedence over locale-dictated
    # formats.
    @ignore_warnings(category=RemovedInDjango50Warning)
    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=',')
    def test_decimalfield_support_decimal_separator(self):
        f = FloatField(localize=True)
        self.assertEqual(f.clean('1001,10'), 1001.10)
        self.assertEqual(f.clean('1001.10'), 1001.10)

    # RemovedInDjango50Warning: When the deprecation ends, remove
    # @ignore_warnings and USE_L10N=False. The test should remain because
    # format-related settings will take precedence over locale-dictated
    # formats.
    @ignore_warnings(category=RemovedInDjango50Warning)
    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=',', USE_THOUSAND_SEPARATOR=True,
                       THOUSAND_SEPARATOR='.')
    def test_decimalfield_support_thousands_separator(self):
        """
        Test the support for thousands separator in the FloatField.
        
        This function tests the FloatField's ability to handle a thousands separator
        when the 'localize' attribute is set to True. It checks if the field can
        correctly parse a string with a comma as the thousands separator and a period
        as the decimal separator.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string cannot be parsed as a valid float.
        
        Key Points:
        - The function uses the
        """

        f = FloatField(localize=True)
        self.assertEqual(f.clean('1.001,10'), 1001.10)
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('1,001.1')
