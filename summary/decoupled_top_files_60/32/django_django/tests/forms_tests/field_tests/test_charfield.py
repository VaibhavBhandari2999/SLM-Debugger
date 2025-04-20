from django.forms import (
    CharField, HiddenInput, PasswordInput, Textarea, TextInput,
    ValidationError,
)
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class CharFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_charfield_1(self):
        """
        Test the CharField class.
        
        This function tests various aspects of the CharField class, including:
        - Cleaning integer and string inputs.
        - Handling of required fields.
        - Cleaning of non-string inputs.
        - Checking for the presence of max_length and min_length attributes.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function is used for testing and does not return any value.
        
        Raises:
        - ValidationError: When the input is not a valid string or is empty and the field is
        """

        f = CharField()
        self.assertEqual('1', f.clean(1))
        self.assertEqual('hello', f.clean('hello'))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        self.assertEqual('[1, 2, 3]', f.clean([1, 2, 3]))
        self.assertIsNone(f.max_length)
        self.assertIsNone(f.min_length)

    def test_charfield_2(self):
        f = CharField(required=False)
        self.assertEqual('1', f.clean(1))
        self.assertEqual('hello', f.clean('hello'))
        self.assertEqual('', f.clean(None))
        self.assertEqual('', f.clean(''))
        self.assertEqual('[1, 2, 3]', f.clean([1, 2, 3]))
        self.assertIsNone(f.max_length)
        self.assertIsNone(f.min_length)

    def test_charfield_3(self):
        """
        Test CharField with specified max_length and required=False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - max_length (int): The maximum number of characters allowed in the field.
        - required (bool): Whether the field is required or not. Default is False.
        
        Key Behavior:
        - Validates and returns the input string if it is within the max_length.
        - Raises ValidationError if the input string exceeds the max_length.
        - Returns None for min_length as it
        """

        f = CharField(max_length=10, required=False)
        self.assertEqual('12345', f.clean('12345'))
        self.assertEqual('1234567890', f.clean('1234567890'))
        msg = "'Ensure this value has at most 10 characters (it has 11).'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('1234567890a')
        self.assertEqual(f.max_length, 10)
        self.assertIsNone(f.min_length)

    def test_charfield_4(self):
        f = CharField(min_length=10, required=False)
        self.assertEqual('', f.clean(''))
        msg = "'Ensure this value has at least 10 characters (it has 5).'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('12345')
        self.assertEqual('1234567890', f.clean('1234567890'))
        self.assertEqual('1234567890a', f.clean('1234567890a'))
        self.assertIsNone(f.max_length)
        self.assertEqual(f.min_length, 10)

    def test_charfield_5(self):
        """
        Tests the CharField validation with specified min_length and required=True.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input is empty or does not meet the minimum length requirement.
        
        Key Parameters:
        - min_length (int): The minimum number of characters required for the field.
        - required (bool): Indicates whether the field is required.
        
        Key Steps:
        1. Creates a CharField instance with min_length set to 10 and required set to True.
        2
        """

        f = CharField(min_length=10, required=True)
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        msg = "'Ensure this value has at least 10 characters (it has 5).'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('12345')
        self.assertEqual('1234567890', f.clean('1234567890'))
        self.assertEqual('1234567890a', f.clean('1234567890a'))
        self.assertIsNone(f.max_length)
        self.assertEqual(f.min_length, 10)

    def test_charfield_length_not_int(self):
        """
        Setting min_length or max_length to something that is not a number
        raises an exception.
        """
        with self.assertRaises(ValueError):
            CharField(min_length='a')
        with self.assertRaises(ValueError):
            CharField(max_length='a')
        msg = '__init__() takes 1 positional argument but 2 were given'
        with self.assertRaisesMessage(TypeError, msg):
            CharField('a')

    def test_charfield_widget_attrs(self):
        """
        CharField.widget_attrs() always returns a dictionary and includes
        minlength/maxlength if min_length/max_length are defined on the field
        and the widget is not hidden.
        """
        # Return an emp
