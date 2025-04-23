import decimal

from django.core.exceptions import ValidationError
from django.forms import DecimalField, NumberInput, Widget
from django.test import SimpleTestCase, ignore_warnings, override_settings
from django.utils import formats, translation
from django.utils.deprecation import RemovedInDjango50Warning

from . import FormFieldAssertionsMixin


class DecimalFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_decimalfield_1(self):
        """
        Test for the DecimalField.
        
        This function tests various functionalities of the DecimalField, including:
        - Widget rendering
        - Validation of empty and null inputs
        - Correct conversion and validation of valid inputs
        - Handling of invalid inputs with specific error messages
        
        Key Parameters:
        - max_digits (int): The maximum number of digits the field can hold.
        - decimal_places (int): The number of decimal places the field can hold.
        
        Output:
        - The function does not return anything. It asserts the expected behavior of
        """

        f = DecimalField(max_digits=4, decimal_places=2)
        self.assertWidgetRendersTo(
            f, '<input id="id_f" step="0.01" type="number" name="f" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(f.clean("1"), decimal.Decimal("1"))
        self.assertIsInstance(f.clean("1"), decimal.Decimal)
        self.assertEqual(f.clean("23"), decimal.Decimal("23"))
        self.assertEqual(f.clean("3.14"), decimal.Decimal("3.14"))
        self.assertEqual(f.clean(3.14), decimal.Decimal("3.14"))
        self.assertEqual(f.clean(decimal.Decimal("3.14")), decimal.Decimal("3.14"))
        self.assertEqual(f.clean("1.0 "), decimal.Decimal("1.0"))
        self.assertEqual(f.clean(" 1.0"), decimal.Decimal("1.0"))
        self.assertEqual(f.clean(" 1.0 "), decimal.Decimal("1.0"))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 4 digits in total.'"
        ):
            f.clean("123.45")
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 2 decimal places.'"
        ):
            f.clean("1.234")
        msg = "'Ensure that there are no more than 2 digits before the decimal point.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("123.4")
        self.assertEqual(f.clean("-12.34"), decimal.Decimal("-12.34"))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 4 digits in total.'"
        ):
            f.clean("-123.45")
        self.assertEqual(f.clean("-.12"), decimal.Decimal("-0.12"))
        self.assertEqual(f.clean("-00.12"), decimal.Decimal("-0.12"))
        self.assertEqual(f.clean("-000.12"), decimal.Decimal("-0.12"))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 2 decimal places.'"
        ):
            f.clean("-000.123")
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 4 digits in total.'"
        ):
            f.clean("-000.12345")
        self.assertEqual(f.max_digits, 4)
        self.assertEqual(f.decimal_places, 2)
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_enter_a_number_error(self):
        f = DecimalField(max_value=1, max_digits=4, decimal_places=2)
        values = (
            "-NaN",
            "NaN",
            "+NaN",
            "-sNaN",
            "sNaN",
            "+sNaN",
            "-Inf",
            "Inf",
            "+Inf",
            "-Infinity",
            "Infinity",
            "+Infinity",
            "a",
            "łąść",
            "1.0a",
            "--0.12",
        )
        for value in values:
            with self.subTest(value=value), self.assertRaisesMessage(
                ValidationError, "'Enter a number.'"
            ):
                f.clean(value)

    def test_decimalfield_2(self):
        f = DecimalField(max_digits=4, decimal_places=2, required=False)
        self.assertIsNone(f.clean(""))
        self.assertIsNone(f.clean(None))
        self.assertEqual(f.clean("1"), decimal.Decimal("1"))
        self.assertEqual(f.max_digits, 4)
        self.assertEqual(f.decimal_places, 2)
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_decimalfield_3(self):
        f = DecimalField(
            max_digits=4,
            decimal_places=2,
            max_value=decimal.Decimal("1.5"),
            min_value=decimal.Decimal("0.5"),
        )
        self.assertWidgetRendersTo(
            f,
            '<input step="0.01" name="f" min="0.5" max="1.5" type="number" id="id_f" '
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
        self.assertEqual(f.clean("1.5"), decimal.Decimal("1.5"))
        self.assertEqual(f.clean("0.5"), decimal.Decimal("0.5"))
        self.assertEqual(f.clean(".5"), decimal.Decimal("0.5"))
        self.assertEqual(f.clean("00.50"), decimal.Decimal("0.50"))
        self.assertEqual(f.max_digits, 4)
        self.assertEqual(f.decimal_places, 2)
        self.assertEqual(f.max_value, decimal.Decimal("1.5"))
        self.assertEqual(f.min_value, decimal.Decimal("0.5"))

    def test_decimalfield_4(self):
        f = DecimalField(decimal_places=2)
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 2 decimal places.'"
        ):
            f.clean("0.00000001")

    def test_decimalfield_5(self):
        f = DecimalField(max_digits=3)
        # Leading whole zeros "collapse" to one digit.
        self.assertEqual(f.clean("0000000.10"), decimal.Decimal("0.1"))
        # But a leading 0 before the . doesn't count toward max_digits
        self.assertEqual(f.clean("0000000.100"), decimal.Decimal("0.100"))
        # Only leading whole zeros "collapse" to one digit.
        self.assertEqual(f.clean("000000.02"), decimal.Decimal("0.02"))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 3 digits in total.'"
        ):
            f.clean("000000.0002")
        self.assertEqual(f.clean(".002"), decimal.Decimal("0.002"))

    def test_decimalfield_6(self):
        """
        Test for DecimalField with max_digits=2 and decimal_places=2.
        
        This test checks the behavior of the DecimalField when cleaning input values.
        - Parameters:
        - None (The function uses predefined parameters within its body)
        - Input:
        - A string representing a decimal number
        - Output:
        - A decimal.Decimal object if the input is valid
        - Raises ValidationError with a specific error message if the input is invalid
        
        Key points:
        - The function tests the cleaning of a valid decimal
        """

        f = DecimalField(max_digits=2, decimal_places=2)
        self.assertEqual(f.clean(".01"), decimal.Decimal(".01"))
        msg = "'Ensure that there are no more than 0 digits before the decimal point.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("1.1")

    def test_decimalfield_scientific(self):
        f = DecimalField(max_digits=4, decimal_places=2)
        with self.assertRaisesMessage(ValidationError, "Ensure that there are no more"):
            f.clean("1E+2")
        self.assertEqual(f.clean("1E+1"), decimal.Decimal("10"))
        self.assertEqual(f.clean("1E-1"), decimal.Decimal("0.1"))
        self.assertEqual(f.clean("0.546e+2"), decimal.Decimal("54.6"))

    def test_decimalfield_widget_attrs(self):
        f = DecimalField(max_digits=6, decimal_places=2)
        self.assertEqual(f.widget_attrs(Widget()), {})
        self.assertEqual(f.widget_attrs(NumberInput()), {"step": "0.01"})
        f = DecimalField(max_digits=10, decimal_places=0)
        self.assertEqual(f.widget_attrs(NumberInput()), {"step": "1"})
        f = DecimalField(max_digits=19, decimal_places=19)
        self.assertEqual(f.widget_attrs(NumberInput()), {"step": "1e-19"})
        f = DecimalField(max_digits=20)
        self.assertEqual(f.widget_attrs(NumberInput()), {"step": "any"})
        f = DecimalField(max_digits=6, widget=NumberInput(attrs={"step": "0.01"}))
        self.assertWidgetRendersTo(
            f, '<input step="0.01" name="f" type="number" id="id_f" required>'
        )

    def test_decimalfield_localized(self):
        """
        A localized DecimalField's widget renders to a text input without
        number input specific attributes.
        """
        f = DecimalField(localize=True)
        self.assertWidgetRendersTo(f, '<input id="id_f" name="f" type="text" required>')

    def test_decimalfield_changed(self):
        f = DecimalField(max_digits=2, decimal_places=2)
        d = decimal.Decimal("0.1")
        self.assertFalse(f.has_changed(d, "0.10"))
        self.assertTrue(f.has_changed(d, "0.101"))

        with translation.override("fr"):
            f = DecimalField(max_digits=2, decimal_places=2, localize=True)
            localized_d = formats.localize_input(d)  # -> '0,1' in French
            self.assertFalse(f.has_changed(d, localized_d))

    # RemovedInDjango50Warning: When the deprecation ends, remove
    # @ignore_warnings and USE_L10N=False. The test should remain because
    # format-related settings will take precedence over locale-dictated
    # formats.
    @ignore_warnings(category=RemovedInDjango50Warning)
    @override_settings(USE_L10N=False, DECIMAL_SEPARATOR=",")
    def test_decimalfield_support_decimal_separator(self):
        """
        Tests the DecimalField's support for decimal separators.
        
        This function checks the DecimalField's ability to handle decimal separators in input strings. The field is configured to use localization, which affects how it interprets the decimal separator.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a DecimalField instance with `localize=True`.
        - It tests the `clean` method of the field with two different input strings:
        - "1001,10": This
        """

        f = DecimalField(localize=True)
        self.assertEqual(f.clean("1001,10"), decimal.Decimal("1001.10"))
        self.assertEqual(f.clean("1001.10"), decimal.Decimal("1001.10"))

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
        f = DecimalField(localize=True)
        self.assertEqual(f.clean("1.001,10"), decimal.Decimal("1001.10"))
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("1,001.1")
