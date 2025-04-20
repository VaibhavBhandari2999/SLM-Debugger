import re

from django.forms import RegexField, ValidationError
from django.test import SimpleTestCase


class RegexFieldTest(SimpleTestCase):

    def test_regexfield_1(self):
        """
        Tests the RegexField functionality.
        
        This function validates the RegexField by checking if it correctly matches and cleans input strings according to the specified regular expression pattern. The key parameters include the regular expression pattern used for validation. The function outputs the cleaned string if it matches the pattern, raises a ValidationError with a specific message if the input does not match the pattern, and also checks for empty input.
        
        Parameters:
        None (the function uses a predefined RegexField instance)
        
        Returns:
        None (the function performs assertions
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
        
        This function tests the RegexField with a regular expression that matches a string of the form '[0-9][A-F][0-9]'. The function performs the following checks:
        - Validates that '2A2' and '3F3' are correctly cleaned and returned.
        - Raises a ValidationError with the message "'Enter a valid value.'" when the input is '3G3'.
        - Raises a ValidationError with the message "'Enter a valid value.'" when the
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
        Test changing the regular expression of a RegexField after initialization.
        
        This test checks that modifying the regex attribute of a RegexField instance
        after its initialization affects the validation behavior of the field.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A RegexField instance `f` is created with the initial regex pattern '^[a-z]+$'.
        - The regex pattern is then changed to '^[0-9]+$'.
        - The `clean` method is called with the value
        """

        f = RegexField('^[a-z]+$')
        f.regex = '^[0-9]+$'
        self.assertEqual('1234', f.clean('1234'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('abcd')
