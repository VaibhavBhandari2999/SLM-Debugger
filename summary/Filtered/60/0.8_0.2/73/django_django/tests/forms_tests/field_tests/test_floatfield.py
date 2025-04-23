from django.core.exceptions import ValidationError
from django.forms import FloatField, NumberInput
from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import formats, translation

from . import FormFieldAssertionsMixin


class FloatFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_floatfield_1(self):
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
        """
        Test the FloatField class.
        
        This function tests the FloatField class, which is used to validate and clean input data for floating-point numbers. The function checks the following scenarios:
        - Clean an empty string, which should return None.
        - Clean a None value, which should also return None.
        - Clean a valid float value ('1'), which should return the float value 1.0.
        - Ensure that the max_value and min_value attributes are not set by default.
        
        Parameters:
        - None
        
        Returns
        """

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

        with translation.override('fr'), self.settings(USE_L10N=True):
            f = FloatField(localize=True)
            localized_n = formats.localize_input(n)  # -> '4,35' in French
            self.assertFalse(f.has_changed(n, localized_n))

    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=',')
    def test_decimalfield_support_decimal_separator(self):
        f = FloatField(localize=True)
        self.assertEqual(f.clean('1001,10'), 1001.10)
        self.assertEqual(f.clean('1001.10'), 1001.10)

    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=',', USE_THOUSAND_SEPARATOR=True,
                       THOUSAND_SEPARATOR='.')
    def test_decimalfield_support_thousands_separator(self):
        """
        Tests the support for thousands separator in the FloatField with localization.
        
        This function checks if the FloatField with localization enabled can correctly parse a string with a thousands separator and a decimal point. It also tests the validation error message when an invalid input is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function creates an instance of FloatField with localization set to True.
        - It tests the clean method of the field with a valid input string '1.00
        """

        f = FloatField(localize=True)
        self.assertEqual(f.clean('1.001,10'), 1001.10)
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('1,001.1')
