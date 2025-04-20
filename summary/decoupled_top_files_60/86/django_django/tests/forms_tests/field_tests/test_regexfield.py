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
        1. Validates and confirms the correct input '2A2' and '3F3' by calling the `clean` method.
        2. Raises a ValidationError with the message "'Enter a valid value.'" for invalid inputs '3G3
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
        Tests the RegexField functionality.
        
        This function tests the RegexField with a regular expression that matches a string of the form '[0-9][A-F][0-9]'. The function checks if the RegexField correctly validates and cleans input strings that match the pattern, and raises a ValidationError for inputs that do not match the pattern. The function also tests for leading and trailing spaces in valid inputs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: Raised when the input does
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
        Tests the behavior of changing the regex pattern after initialization of a RegexField.
        
        This function creates an instance of RegexField with the initial regex pattern '^[a-z]+$'. It then changes the regex pattern to '^[0-9]+$'. The function asserts that the field correctly validates numeric strings ('1234') and raises a ValidationError for non-numeric strings ('abcd').
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the field does not raise a ValidationError
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
        f = RegexField('^[a-z]+$', strip=True)
        self.assertEqual(f.clean(' a'), 'a')
        self.assertEqual(f.clean('a '), 'a')

    def test_empty_value(self):
        f = RegexField('', required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = RegexField('', empty_value=None, required=False)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
      self.assertIsNone(f.clean(None))
