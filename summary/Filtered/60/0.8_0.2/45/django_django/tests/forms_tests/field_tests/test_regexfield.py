import re

from django.core.exceptions import ValidationError
from django.forms import RegexField
from django.test import SimpleTestCase


class RegexFieldTest(SimpleTestCase):

    def test_regexfield_1(self):
        """
        Tests the RegexField functionality.
        
        This function tests the RegexField with the following key parameters:
        - `f`: A RegexField instance with the regular expression pattern '^[0-9][A-F][0-9]$'.
        
        The function performs the following actions:
        1. Validates and asserts that '2A2' and '3F3' are correctly cleaned by the RegexField.
        2. Raises a ValidationError with the message "'Enter a valid value.'" for inputs '3G3', '
        """

        f = RegexField('^[0-9][A-F][0-9]$')
        self.assertEqual('2A2', f.clean('2A2'))
        self.assertEqual('3F3', f.clean('3F3'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('3G3')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean(' 2A2')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('2A2 ')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')

    def test_regexfield_2(self):
        f = RegexField('^[0-9][A-F][0-9]$', required=False)
        self.assertEqual('2A2', f.clean('2A2'))
        self.assertEqual('3F3', f.clean('3F3'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('3G3')
        self.assertEqual('', f.clean(''))

    def test_regexfield_3(self):
        """
        Tests the behavior of the RegexField with specific validation rules.
        
        This function tests the RegexField with a regular expression that matches a string of the form '[0-9][A-F][0-9]'. It validates that the field correctly accepts valid inputs and raises a ValidationError for invalid inputs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The RegexField is initialized with a regular expression pattern.
        - The function tests the field's clean method with valid and invalid inputs
        """

        f = RegexField(re.compile('^[0-9][A-F][0-9]$'))
        self.assertEqual('2A2', f.clean('2A2'))
        self.assertEqual('3F3', f.clean('3F3'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('3G3')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean(' 2A2')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('2A2 ')

    def test_regexfield_4(self):
        f = RegexField('^[0-9]+$', min_length=5, max_length=10)
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at least 5 characters (it has 3).'"):
            f.clean('123')
        with self.assertRaisesMessage(
            ValidationError,
            "'Ensure this value has at least 5 characters (it has 3).', "
            "'Enter a valid value.'",
        ):
            f.clean('abc')
        self.assertEqual('12345', f.clean('12345'))
        self.assertEqual('1234567890', f.clean('1234567890'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value has at most 10 characters (it has 11).'"):
            f.clean('12345678901')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('12345a')

    def test_regexfield_unicode_characters(self):
        f = RegexField(r'^\w+$')
        self.assertEqual('éèøçÎÎ你好', f.clean('éèøçÎÎ你好'))

    def test_change_regex_after_init(self):
        """
        Tests the behavior of changing the regex pattern after initializing a RegexField.
        
        This function creates an instance of RegexField with a specific regex pattern and then changes the regex pattern. It then tests the clean method to ensure that it behaves as expected based on the new regex pattern.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Initializes a RegexField with a regex pattern of '^[a-z]+$'.
        - Changes the regex pattern to '^[0-9]+$'.
        -
        """

        f = RegexField('^[a-z]+$')
        f.regex = '^[0-9]+$'
        self.assertEqual('1234', f.clean('1234'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('abcd')

    def test_get_regex(self):
        f = RegexField('^[a-z]+$')
        self.assertEqual(f.regex, re.compile('^[a-z]+$'))

    def test_regexfield_strip(self):
        """
        Tests the RegexField with strip=True functionality.
        
        This function checks the RegexField's ability to strip whitespace from the input string before applying the regular expression validation. The key parameters are:
        - `f`: A RegexField instance with the regular expression '^[a-z]+$' and strip=True.
        
        The function does not return any value but asserts the following:
        - 'a' is the expected output when ' a' is passed to the clean method.
        - 'a' is the expected output when 'a
        """

        f = RegexField('^[a-z]+$', strip=True)
        self.assertEqual(f.clean(' a'), 'a')
        self.assertEqual(f.clean('a '), 'a')
