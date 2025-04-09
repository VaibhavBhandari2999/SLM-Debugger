"""
The provided Python file contains a test suite for the `RegexField` class from Django's forms module. The suite includes various test cases to ensure that the `RegexField` behaves as expected under different conditions:

- **RegexFieldTest Class**: Defines multiple test methods (`test_regexfield_1`, `test_regexfield_2`, etc.) to validate the `RegexField`'s functionality. Each test method focuses on specific aspects such as validation rules, handling of empty strings, and custom regular expressions.

- **Key Responsibilities**:
  - Validates input strings against a specified regular expression.
  - Cleans input strings according to the defined pattern.
  - Raises `ValidationError` for invalid inputs.
  - Handles edge cases like empty strings, whitespace
"""
import re

from django.core.exceptions import ValidationError
from django.forms import RegexField
from django.test import SimpleTestCase


class RegexFieldTest(SimpleTestCase):

    def test_regexfield_1(self):
        """
        Tests the behavior of the RegexField with various inputs.
        
        This function tests the validation and cleaning capabilities of the RegexField
        using different input values. It checks if the field correctly validates and
        cleans valid input strings, raises ValidationError for invalid inputs, and
        handles empty string inputs.
        
        Args:
        None (The function uses a predefined instance of RegexField).
        
        Returns:
        None (The function asserts expected outcomes).
        
        Important Functions:
        - `clean`: Validates and cleans
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
        """
        Tests the behavior of the RegexField with specific validation rules.
        
        This function creates an instance of RegexField with a defined regular expression pattern and tests its validation logic. The field is configured to match strings that start with a digit, followed by a hexadecimal character (A-F), and end with another digit. It also handles cases where the input is empty or invalid.
        
        Args:
        None
        
        Returns:
        None
        
        Methods:
        - clean: Validates the input string against the regex pattern
        """

        f = RegexField('^[0-9][A-F][0-9]$', required=False)
        self.assertEqual('2A2', f.clean('2A2'))
        self.assertEqual('3F3', f.clean('3F3'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid value.'"):
            f.clean('3G3')
        self.assertEqual('', f.clean(''))

    def test_regexfield_3(self):
        """
        Tests the behavior of the RegexField with specific regular expression validation.
        
        This function creates an instance of RegexField with a given regular expression pattern and performs several tests on it. The field is expected to validate input strings based on the provided regex pattern and raise ValidationError for invalid inputs.
        
        Args:
        None (This function is part of a test suite and does not take any arguments).
        
        Returns:
        None (This function performs assertions and does not return any value).
        
        Important Functions and Variables:
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
        """
        Tests the behavior of the RegexField with specified regular expression, minimum length, and maximum length constraints.
        
        - Validates that values shorter than the minimum length raise a ValidationError with an appropriate message.
        - Validates that invalid values raise a ValidationError with multiple messages.
        - Validates that valid values within the specified length range are returned as is.
        - Validates that values longer than the maximum length raise a ValidationError with an appropriate message.
        - Validates that values containing invalid characters raise a ValidationError with an appropriate message
        """

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
        Tests the behavior of changing the regular expression pattern of a RegexField after initialization.
        
        This function initializes a RegexField with a lowercase letter pattern, then changes it to a digit pattern.
        It verifies that the field correctly validates inputs based on the updated pattern.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `RegexField`: Initializes the field with a given regex pattern.
        - `f.regex = '^[0-9]+$'`: Changes the regex
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
        Tests the `clean` method of a RegexField with the `strip` parameter set to True.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        - Field type: RegexField
        - Regular expression: '^[a-z]+$'
        - Input strings: ' a', 'a '
        - Output strings: 'a', 'a'
        - Functionality: Strips whitespace from input strings before applying the regular expression check.
        """

        f = RegexField('^[a-z]+$', strip=True)
        self.assertEqual(f.clean(' a'), 'a')
        self.assertEqual(f.clean('a '), 'a')

    def test_empty_value(self):
        """
        Tests the behavior of the RegexField when given an empty value or None.
        
        This function checks how the RegexField handles empty strings and None values,
        specifically focusing on the `clean` method. It creates instances of RegexField
        with different configurations (empty_value set to '' or None) and verifies that
        the `clean` method returns the expected outputs.
        
        Args:
        No explicit arguments are passed; instead, the function uses instance attributes.
        
        Returns:
        None: The
        """

        f = RegexField('', required=False)
        self.assertEqual(f.clean(''), '')
        self.assertEqual(f.clean(None), '')
        f = RegexField('', empty_value=None, required=False)
        self.assertIsNone(f.clean(''))
        self.assertIsNone(f.clean(None))
