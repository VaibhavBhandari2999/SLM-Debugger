import re

from django.core.exceptions import ValidationError
from django.forms import RegexField
from django.test import SimpleTestCase


class RegexFieldTest(SimpleTestCase):
    def test_regexfield_1(self):
        """
        Tests the RegexField functionality.
        
        This function tests the RegexField with a specific regular expression pattern. The field is expected to validate and return values that match the pattern "^[0-9][A-F][0-9]$". The function performs the following checks:
        - Validates and returns "2A2" and "3F3" as expected.
        - Raises a ValidationError with the message "'Enter a valid value.'" for inputs "3G3", " 2A2", "2A
        """

        f = RegexField("^[0-9][A-F][0-9]$")
        self.assertEqual("2A2", f.clean("2A2"))
        self.assertEqual("3F3", f.clean("3F3"))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("3G3")
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean(" 2A2")
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("2A2 ")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")

    def test_regexfield_2(self):
        f = RegexField("^[0-9][A-F][0-9]$", required=False)
        self.assertEqual("2A2", f.clean("2A2"))
        self.assertEqual("3F3", f.clean("3F3"))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("3G3")
        self.assertEqual("", f.clean(""))

    def test_regexfield_3(self):
        f = RegexField(re.compile("^[0-9][A-F][0-9]$"))
        self.assertEqual("2A2", f.clean("2A2"))
        self.assertEqual("3F3", f.clean("3F3"))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("3G3")
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean(" 2A2")
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("2A2 ")

    def test_regexfield_4(self):
        f = RegexField("^[0-9]+$", min_length=5, max_length=10)
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value has at least 5 characters (it has 3).'"
        ):
            f.clean("123")
        with self.assertRaisesMessage(
            ValidationError,
            "'Ensure this value has at least 5 characters (it has 3).', "
            "'Enter a valid value.'",
        ):
            f.clean("abc")
        self.assertEqual("12345", f.clean("12345"))
        self.assertEqual("1234567890", f.clean("1234567890"))
        with self.assertRaisesMessage(
            ValidationError,
            "'Ensure this value has at most 10 characters (it has 11).'",
        ):
            f.clean("12345678901")
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("12345a")

    def test_regexfield_unicode_characters(self):
        f = RegexField(r"^\w+$")
        self.assertEqual("éèøçÎÎ你好", f.clean("éèøçÎÎ你好"))

    def test_change_regex_after_init(self):
        """
        Tests the behavior of changing the regex attribute after the RegexField instance is initialized.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Initializes a RegexField instance with the regex pattern "^[a-z]+$".
        2. Changes the regex pattern to "^[0-9]+$".
        3. Asserts that the clean method returns "1234" when "1234" is passed as input.
        4. Asserts that a ValidationError is raised with the message "
        """

        f = RegexField("^[a-z]+$")
        f.regex = "^[0-9]+$"
        self.assertEqual("1234", f.clean("1234"))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean("abcd")

    def test_get_regex(self):
        f = RegexField("^[a-z]+$")
        self.assertEqual(f.regex, re.compile("^[a-z]+$"))

    def test_regexfield_strip(self):
        f = RegexField("^[a-z]+$", strip=True)
        self.assertEqual(f.clean(" a"), "a")
        self.assertEqual(f.clean("a "), "a")

    def test_empty_value(self):
        """
        Tests the behavior of the RegexField when provided with empty or None values.
        
        This function tests the RegexField with empty strings and None values to ensure that it handles them correctly based on the provided parameters.
        
        Parameters:
        f (RegexField): The RegexField instance to be tested.
        
        Returns:
        None: This function does not return any value. It asserts the expected behavior of the RegexField.
        
        Key Parameters:
        - f: The RegexField instance to test. It can be configured with different parameters
        """

        f = RegexField("", required=False)
        self.assertEqual(f.clean(""), "")
        self.assertEqual(f.clean(None), "")
        f = RegexField("", empty_value=None, required=False)
        self.assertIsNone(f.clean(""))
        self.assertIsNone(f.clean(None))
