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
        Tests the behavior of the DecimalField with specified max_digits and decimal_places. The function validates input values based on the defined constraints and handles various edge cases such as empty strings, None, and incorrect formats. It also checks the cleaning process and ensures that the cleaned value is a Decimal instance. The function raises ValidationError for inputs that do not meet the criteria.
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
        """
        Tests the validation of non-numeric inputs for a DecimalField with max_value=1, max_digits=4, and decimal_places=2. The function iterates through a list of invalid values and asserts that each raises a ValidationError with the message 'Enter a number.' The affected functions include DecimalField and ValidationError.
        """

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
        """
        Tests the behavior of the DecimalField with various inputs and configurations.
        
        This function tests the DecimalField by validating its clean method with empty strings, None values, and a valid decimal value. It also checks the max_digits, decimal_places, and absence of min_value and max_value constraints.
        
        Args:
        None (The function is a test case and does not take any arguments).
        
        Returns:
        None (The function asserts conditions and does not return any value).
        
        Important
        """

        f = DecimalField(max_digits=4, decimal_places=2, required=False)
        self.assertIsNone(f.clean(""))
        self.assertIsNone(f.clean(None))
        self.assertEqual(f.clean("1"), decimal.Decimal("1"))
        self.assertEqual(f.max_digits, 4)
        self.assertEqual(f.decimal_places, 2)
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_decimalfield_3(self):
        """
        Tests the behavior of a DecimalField with specified max_digits, decimal_places, max_value, and min_value. The field is expected to render an HTML <input> element with number type, step size of 0.01, and appropriate min and max attributes. It validates input values against the defined constraints, converting strings to Decimal objects where necessary. The field's properties such as max_digits, decimal_places, max_value, and min_value are also verified.
        
        Args:
        None
        """

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
        """
        Tests the validation of a DecimalField with decimal_places set to 2. Ensures that the field raises a ValidationError if the input has more than 2 decimal places.
        
        Args:
        None (The method is a test case and does not take any arguments).
        
        Raises:
        ValidationError: If the input value has more than 2 decimal places.
        
        Usage:
        This method can be used to verify that the DecimalField correctly enforces the specified decimal_places constraint.
        """

        f = DecimalField(decimal_places=2)
        with self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 2 decimal places.'"
        ):
            f.clean("0.00000001")

    def test_decimalfield_5(self):
        """
        Tests the behavior of the DecimalField with specified max_digits.
        
        - Validates that leading whole zeros collapse to one digit.
        - Ensures that a leading '0' before the '.' does not count towards max_digits.
        - Checks that only leading whole zeros collapse to one digit.
        - Raises a ValidationError if there are more than 3 digits in total.
        - Cleans and returns decimal.Decimal objects.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        -
        """

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
        Tests the validation of a DecimalField with max_digits=2 and decimal_places=2. The clean method is used to validate the input ".01" which passes successfully. An attempt to validate "1.1" raises a ValidationError with the specified error message.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - DecimalField: Defines the field with specified max_digits and decimal_places.
        - clean: Validates the input value.
        - assertEqual: Comp
        """

        f = DecimalField(max_digits=2, decimal_places=2)
        self.assertEqual(f.clean(".01"), decimal.Decimal(".01"))
        msg = "'Ensure that there are no more than 0 digits before the decimal point.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("1.1")

    def test_decimalfield_scientific(self):
        """
        Tests the behavior of the DecimalField with scientific notation inputs.
        
        This function tests the DecimalField's ability to handle scientific notation
        inputs by cleaning and validating them. It uses the `clean` method of the
        DecimalField to process different scientific notation strings and ensures
        that the cleaned values match the expected decimal.Decimal objects.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string does not conform to the expected
        format or
        """

        f = DecimalField(max_digits=4, decimal_places=2)
        with self.assertRaisesMessage(ValidationError, "Ensure that there are no more"):
            f.clean("1E+2")
        self.assertEqual(f.clean("1E+1"), decimal.Decimal("10"))
        self.assertEqual(f.clean("1E-1"), decimal.Decimal("0.1"))
        self.assertEqual(f.clean("0.546e+2"), decimal.Decimal("54.6"))

    def test_decimalfield_widget_attrs(self):
        """
        Tests the attributes generated by DecimalField for different configurations of max_digits and decimal_places. The function checks how the widget attributes are set based on the field configuration and the widget used. It verifies the 'step' attribute for NumberInput widgets with various settings of max_digits and decimal_places, and also considers custom step values passed through widget attrs.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DecimalField`: Configures the decimal field with specified max_digits and
        """

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
        """
        Tests the behavior of the `has_changed` method for a DecimalField.
        
        This method checks whether a Decimal value has changed, considering both
        unlocalized and localized inputs. It uses the `DecimalField`, `decimal.Decimal`,
        and `formats.localize_input` functions to compare the original and new values.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DecimalField`: Defines the field with specified `max_digits` and `decimal_places`.
        """

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
        Tests the support for decimal separators in DecimalField.
        
        This function checks if the DecimalField with `localize=True` correctly handles
        both comma (',') and dot ('.') as decimal separators when cleaning input values.
        It uses the `clean` method of the DecimalField to convert string inputs into
        Decimal objects.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - DecimalField: A field type that stores and validates decimal numbers.
        -
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
        """
        Tests the support for thousands separator in DecimalField with localization enabled.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DecimalField(localize=True)`: Creates a DecimalField instance with localization enabled.
        - `clean(value)`: Cleans and validates the input value.
        - `assertEqual(expected, actual)`: Compares the expected and actual results.
        - `assertRaisesMessage(context_manager, message)`: Asserts that a specific ValidationError message is
        """

        f = DecimalField(localize=True)
        self.assertEqual(f.clean("1.001,10"), decimal.Decimal("1001.10"))
        msg = "'Enter a number.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("1,001.1")
