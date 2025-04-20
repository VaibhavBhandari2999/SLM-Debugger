from django.forms import IntegerField, Textarea, ValidationError
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class IntegerFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_integerfield_1(self):
        """
        Tests the IntegerField class.
        
        This function tests various functionalities of the IntegerField class, including:
        - Widget rendering
        - Required field validation
        - Integer value cleaning and conversion
        - Validation of non-integer inputs
        - Handling of whitespace in input
        - Absence of max_value and min_value constraints
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: When the input is not a valid integer or when the field is required but no input is provided.
        
        Key Points:
        -
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
        Tests the IntegerField with specified min_value and max_value constraints.
        
        This function tests the IntegerField with a minimum value of 10 and a maximum value of 20. It checks the rendering of the widget, validation of required fields, and the handling of valid and invalid input values.
        
        Key Parameters:
        - None (The function does not take any parameters)
        
        Key Attributes:
        - min_value (int): The minimum allowed value for the field.
        - max_value (int): The maximum allowed value
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
        Test the clean method of the IntegerField for handling large integer values.
        
        This function tests the clean method of the IntegerField to ensure it correctly handles large integer values, including both integer and string inputs, as well as floating point strings. The function expects the clean method to return the input value as an integer.
        
        Parameters:
        - f (IntegerField): The IntegerField instance to test.
        
        Returns:
        - int: The cleaned integer value.
        
        Test Cases:
        - 922337203
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
