from django.core.exceptions import ValidationError
from django.forms import FloatField, NumberInput
from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import formats, translation

from . import FormFieldAssertionsMixin


class FloatFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_floatfield_1(self):
        """
        Tests the behavior of the FloatField in Django forms.
        
        This function tests the FloatField in Django forms to ensure it behaves as expected. Key aspects tested include:
        - Widget rendering
        - Required field validation
        - Valid and invalid input handling
        - Precision and formatting
        - Handling of special floating point values
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: When invalid input is provided or validation fails.
        
        Key Points:
        - The field is rendered with a number input type with step
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
        """
        Tests the behavior of the FloatField with specified max_value and min_value constraints.
        
        This function tests the FloatField with a maximum value of 1.5 and a minimum value of 0.5. It checks the rendering of the widget, validation of input values, and the handling of the maximum and minimum values.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - max_value (float): The maximum allowed value for the field.
        - min_value (float): The minimum allowed value for the field
        """

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
        """
        Tests the behavior of the `has_changed` method for a FloatField.
        
        This method checks whether a float value has changed, considering both unlocalized and localized input values. It ensures that the method correctly identifies no change when the input value matches the original value, even when the input is provided in a localized format.
        
        Parameters:
        f (FloatField): The FloatField instance to test.
        n (float): The original float value.
        
        Returns:
        bool: False if the value has not changed
        """

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
        f = FloatField(localize=True)
        self.assertEqual(f.clean('1.001,10'), 1001.10)
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('1,001.1')
