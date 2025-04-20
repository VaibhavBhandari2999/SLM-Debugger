from django.core.exceptions import ValidationError
from django.forms import FloatField, NumberInput
from django.test import SimpleTestCase
from django.test.selenium import SeleniumTestCase
from django.test.utils import ignore_warnings, override_settings
from django.urls import reverse
from django.utils import formats, translation
from django.utils.deprecation import RemovedInDjango50Warning

from . import FormFieldAssertionsMixin


class FloatFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_floatfield_1(self):
        """
        Test the FloatField functionality.
        
        This test function checks the behavior of the FloatField in various scenarios:
        - Widget rendering: Ensures the input widget is correctly rendered with the appropriate attributes.
        - Required field validation: Verifies that the field raises a ValidationError when left empty or set to None.
        - Value conversion: Confirms that the field correctly converts string representations of numbers to float.
        - Precision and formatting: Validates that the field handles floating point precision and whitespace correctly.
        - Error handling: Tests that the
        """

        f = FloatField()
        self.assertWidgetRendersTo(
            f, '<input step="any" type="number" name="f" id="id_f" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1.0, f.clean("1"))
        self.assertIsInstance(f.clean("1"), float)
        self.assertEqual(23.0, f.clean("23"))
        self.assertEqual(3.1400000000000001, f.clean("3.14"))
        self.assertEqual(3.1400000000000001, f.clean(3.14))
        self.assertEqual(42.0, f.clean(42))
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean("a")
        self.assertEqual(1.0, f.clean("1.0 "))
        self.assertEqual(1.0, f.clean(" 1.0"))
        self.assertEqual(1.0, f.clean(" 1.0 "))
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean("1.0a")
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean("Infinity")
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean("NaN")
        with self.assertRaisesMessage(ValidationError, "'Enter a number.'"):
            f.clean("-Inf")

    def test_floatfield_2(self):
        f = FloatField(required=False)
        self.assertIsNone(f.clean(""))
        self.assertIsNone(f.clean(None))
        self.assertEqual(1.0, f.clean("1"))
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_floatfield_3(self):
        f = FloatField(max_value=1.5, min_value=0.5)
        self.assertWidgetRendersTo(
            f,
            '<input step="any" name="f" min="0.5" max="1.5" type="number" id="id_f" '
            "required>",
        )
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is less than or equal to 1.5.'"
        ):
            f.clean("1.6")
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is greater than or equal to 0.5.'"
        ):
            f.clean("0.4")
        self.assertEqual(1.5, f.clean("1.5"))
        self.assertEqual(0.5, f.clean("0.5"))
        self.assertEqual(f.max_value, 1.5)
        self.assertEqual(f.min_value, 0.5)

    def test_floatfield_4(self):
        """
        Test the FloatField with a step size of 0.02.
        
        This test function verifies the behavior of a FloatField with a specified step size of 0.02. It checks the rendering of the field in HTML, the validation of input values, and the cleaning process of valid and invalid inputs.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The field is rendered with the 'step' attribute set to 0.02.
        - The field is required
        """

        f = FloatField(step_size=0.02)
        self.assertWidgetRendersTo(
            f,
            '<input name="f" step="0.02" type="number" id="id_f" required>',
        )
        msg = "'Ensure this value is a multiple of step size 0.02.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("0.01")
        self.assertEqual(2.34, f.clean("2.34"))
        self.assertEqual(2.1, f.clean("2.1"))
        self.assertEqual(-0.50, f.clean("-.5"))
        self.assertEqual(-1.26, f.clean("-1.26"))
        self.assertEqual(f.step_size, 0.02)

    def test_floatfield_widget_attrs(self):
        """
        Tests the rendering of a FloatField with a NumberInput widget, specifying custom attributes such as step, max, and min. The function asserts that the rendered HTML input tag matches the expected attributes and structure.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - step: The step increment for the number input (0.01 in this case).
        - max: The maximum value allowed (1.0 in this case).
        - min: The minimum value allowed (0
        """

        f = FloatField(widget=NumberInput(attrs={"step": 0.01, "max": 1.0, "min": 0.0}))
        self.assertWidgetRendersTo(
            f,
            '<input step="0.01" name="f" min="0.0" max="1.0" type="number" id="id_f" '
            "required>",
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
        self.assertFalse(f.has_changed(n, "4.3500"))

        with translation.override("fr"):
            f = FloatField(localize=True)
            localized_n = formats.localize_input(n)  # -> '4,35' in French
            self.assertFalse(f.has_changed(n, localized_n))

    # RemovedInDjango50Warning: When the deprecation ends, remove
    # @ignore_warnings and USE_L10N=False. The test should remain because
    # format-related settings will take precedence over locale-dictated
    # formats.
    @ignore_warnings(category=RemovedInDjango50Warning)
    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=",")
    def test_decimalfield_support_decimal_separator(self):
        f = FloatField(localize=True)
        self.assertEqual(f.clean("1001,10"), 1001.10)
        self.assertEqual(f.clean("1001.10"), 1001.10)

    # RemovedInDjango50Warning: When the deprecation ends, remove
    # @ignore_warnings and USE_L10N=False. The test should remain because
    # format-related settings will take precedence over locale-dictated
    # formats.
    @ignore_warnings(category=RemovedInDjango50Warning)
    @override_settings(
        USE_L10N=False,
        DECIMAL_SEPARATOR=",",
        USE_THOUSAND_SEPARATOR=True,
        THOUSAND_SEPARATOR=".",
    )
    def test_decimalfield_support_thousands_separator(self):
        """
        Tests the support for thousands separator in the FloatField with localization enabled.
        
        This function checks if the FloatField correctly handles input with a thousands separator and decimal point. The key parameters are:
        - `f`: The FloatField instance with localization set to True.
        
        The function performs the following actions:
        1. Cleans the input "1.001,10" and expects the output to be 1001.10.
        2. Attempts to clean the input "1,00
        """

        f = FloatField(localize=True)
        self.assertEqual(f.clean("1.001,10"), 1001.10)
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("1,001.1")


@override_settings(ROOT_URLCONF="forms_tests.urls")
class FloatFieldHTMLTest(SeleniumTestCase):

    available_apps = ["forms_tests"]

    def test_float_field_rendering_passes_client_side_validation(self):
        """
        Rendered widget allows non-integer value with the client-side
        validation.
        """
        from selenium.webdriver.common.by import By

        self.selenium.get(self.live_server_url + reverse("form_view"))
        number_input = self.selenium.find_element(By.ID, "id_number")
        number_input.send_keys("0.5")
        is_valid = self.selenium.execute_script(
            "return document.getElementById('id_number').checkValidity()"
        )
        self.assertTrue(is_valid)
'id_number').checkValidity()"
        )
        self.assertTrue(is_valid)
