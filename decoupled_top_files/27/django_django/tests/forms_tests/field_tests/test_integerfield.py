from django.forms import IntegerField, Textarea, ValidationError
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class IntegerFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_integerfield_1(self):
        """
        Tests the behavior of the IntegerField class.
        
        This function verifies that the IntegerField correctly handles various inputs,
        including rendering the appropriate HTML widget, validating required fields,
        converting string inputs to integers, and handling invalid inputs.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - assertWidgetRendersTo: Verifies the rendered HTML widget matches the expected format.
        - clean: Validates and converts input values to integers.
        - ValidationError: Raised when input
        """

        f = IntegerField()
        self.assertWidgetRendersTo(f, '<input type="number" name="f" id="id_f" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1, f.clean('1'))
        self.assertIsInstance(f.clean('1'), int)
        self.assertEqual(23, f.clean('23'))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('a')
        self.assertEqual(42, f.clean(42))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean(3.14)
        self.assertEqual(1, f.clean('1 '))
        self.assertEqual(1, f.clean(' 1'))
        self.assertEqual(1, f.clean(' 1 '))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('1a')
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_integerfield_2(self):
        """
        Tests the behavior of the IntegerField class.
        
        This function tests various aspects of the IntegerField class, including:
        - Cleaning empty strings and None values
        - Validating integer inputs
        - Handling whitespace around integers
        - Raising ValidationError for non-integer inputs
        - Checking default max_value and min_value settings
        
        Args:
        No explicit arguments are required; the test is performed internally.
        
        Returns:
        None: The function does not return any value but asserts the
        """

        f = IntegerField(required=False)
        self.assertIsNone(f.clean(''))
        self.assertEqual('None', repr(f.clean('')))
        self.assertIsNone(f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertEqual(1, f.clean('1'))
        self.assertIsInstance(f.clean('1'), int)
        self.assertEqual(23, f.clean('23'))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('a')
        self.assertEqual(1, f.clean('1 '))
        self.assertEqual(1, f.clean(' 1'))
        self.assertEqual(1, f.clean(' 1 '))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('1a')
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_integerfield_3(self):
        """
        Tests the behavior of an IntegerField with a specified maximum value.
        
        - Validates that the field renders correctly with a maximum attribute.
        - Ensures that the field raises a ValidationError when no value is provided.
        - Confirms that valid integer values (1 and 10) are cleaned and returned as expected.
        - Verifies that values exceeding the maximum value (11) raise a ValidationError.
        - Checks that string representations of valid integers (10 and '10') are
        """

        f = IntegerField(max_value=10)
        self.assertWidgetRendersTo(f, '<input max="10" type="number" name="f" id="id_f" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1, f.clean(1))
        self.assertEqual(10, f.clean(10))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is less than or equal to 10.'"):
            f.clean(11)
        self.assertEqual(10, f.clean('10'))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is less than or equal to 10.'"):
            f.clean('11')
        self.assertEqual(f.max_value, 10)
        self.assertIsNone(f.min_value)

    def test_integerfield_4(self):
        """
        Tests the behavior of an IntegerField with a specified minimum value.
        
        - Validates that the field renders correctly with a number input widget and a specified minimum value attribute.
        - Ensures that the field raises a ValidationError when no value is provided.
        - Verifies that the field raises a ValidationError when a value less than the specified minimum is provided.
        - Confirms that the field correctly returns the specified minimum value when cleaned with that value.
        - Checks that values equal to or greater than the
        """

        f = IntegerField(min_value=10)
        self.assertWidgetRendersTo(f, '<input id="id_f" type="number" name="f" min="10" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is greater than or equal to 10.'"):
            f.clean(1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean('10'))
        self.assertEqual(11, f.clean('11'))
        self.assertIsNone(f.max_value)
        self.assertEqual(f.min_value, 10)

    def test_integerfield_5(self):
        """
        Tests the behavior of an IntegerField with specified min_value and max_value constraints.
        
        - Validates that the widget renders correctly with min and max attributes.
        - Ensures that the field raises a ValidationError when None is passed.
        - Checks that values below the min_value raise a ValidationError.
        - Confirms that the min_value (10) and values above it are accepted.
        - Verifies that values above the max_value raise a ValidationError.
        - Asserts that the max_value (
        """

        f = IntegerField(min_value=10, max_value=20)
        self.assertWidgetRendersTo(f, '<input id="id_f" max="20" type="number" name="f" min="10" required>')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is greater than or equal to 10.'"):
            f.clean(1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean('10'))
        self.assertEqual(11, f.clean('11'))
        self.assertEqual(20, f.clean(20))
        with self.assertRaisesMessage(ValidationError, "'Ensure this value is less than or equal to 20.'"):
            f.clean(21)
        self.assertEqual(f.max_value, 20)
        self.assertEqual(f.min_value, 10)

    def test_integerfield_localized(self):
        """
        A localized IntegerField's widget renders to a text input without any
        number input specific attributes.
        """
        f1 = IntegerField(localize=True)
        self.assertWidgetRendersTo(f1, '<input id="id_f" name="f" type="text" required>')

    def test_integerfield_float(self):
        """
        Tests the clean method of the IntegerField class.
        
        This function verifies that the clean method correctly handles integer values,
        including those represented as floats or strings, and raises a ValidationError
        for non-integer inputs.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - IntegerField.clean: Cleans and validates an input value.
        - assertEqual: Compares expected and actual outputs.
        - assertRaisesMessage: Checks if a specific error message is raised.
        """

        f = IntegerField()
        self.assertEqual(1, f.clean(1.0))
        self.assertEqual(1, f.clean('1.0'))
        self.assertEqual(1, f.clean(' 1.0 '))
        self.assertEqual(1, f.clean('1.'))
        self.assertEqual(1, f.clean(' 1. '))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('1.5')
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean('…')

    def test_integerfield_big_num(self):
        """
        Tests the clean method of the IntegerField class with large integer values.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - IntegerField: The field being tested.
        - clean: Method used to validate and convert input values.
        
        Key Variables:
        - 9223372036854775808: The large integer value used as input and expected output.
        """

        f = IntegerField()
        self.assertEqual(9223372036854775808, f.clean(9223372036854775808))
        self.assertEqual(9223372036854775808, f.clean('9223372036854775808'))
        self.assertEqual(9223372036854775808, f.clean('9223372036854775808.0'))

    def test_integerfield_unicode_number(self):
        f = IntegerField()
        self.assertEqual(50, f.clean('５０'))

    def test_integerfield_subclass(self):
        """
        Class-defined widget is not overwritten by __init__() (#22245).
        """
        class MyIntegerField(IntegerField):
            widget = Textarea

        f = MyIntegerField()
        self.assertEqual(f.widget.__class__, Textarea)
        f = MyIntegerField(localize=True)
        self.assertEqual(f.widget.__class__, Textarea)
