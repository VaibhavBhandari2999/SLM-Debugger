import re

from django.core.exceptions import ValidationError
from django.forms import RegexField
from django.test import SimpleTestCase


class RegexFieldTest(SimpleTestCase):

    def test_regexfield_1(self):
        """
        Tests the RegexField functionality.
        
        This function tests the RegexField with the following key parameters:
        - `f`: A RegexField instance with the regular expression '^[0-9][A-F][0-9]$' to match a specific pattern.
        
        Key functionalities tested:
        - Valid input: '2A2' and '3F3' should be cleaned and returned as is.
        - Invalid input: '3G3', ' 2A2', and '2A2 ' should raise
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
        
        This function validates the behavior of the RegexField with the provided regular expression pattern. The key parameters include the regular expression pattern used for validation. The function checks the following:
        - Whether the field correctly validates and returns a value that matches the pattern.
        - Whether the field raises a ValidationError for values that do not match the pattern.
        - Whether the field raises a ValidationError for values with leading or trailing spaces.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError
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
        
        This function validates the behavior of the RegexField when the strip parameter is set to True. It checks if the field correctly strips leading and trailing whitespace from the input string before applying the regex pattern.
        
        Parameters:
        None (This is a test function and does not take any parameters).
        
        Returns:
        None (This function is used for testing and does not return any value).
        
        Key Points:
        - The RegexField is initialized with a regex pattern '^[a
        """

        f = RegexField('^[a-z]+$', strip=True)
        self.assertEqual(f.clean(' a'), 'a')
        self.assertEqual(f.clean('a '), 'a')
