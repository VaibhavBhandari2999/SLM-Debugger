from django.core.exceptions import ValidationError
from django.forms import IntegerField, Textarea
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class IntegerFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_integerfield_1(self):
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
        Tests the IntegerField class for various input scenarios.
        
        This function tests the IntegerField class with different inputs to ensure it behaves as expected. The key parameters include:
        - `value`: The input string or None to be cleaned by the IntegerField.
        
        The function does not return any value but raises ValidationError for invalid inputs.
        
        Key points:
        - If the input is an empty string or None, the function returns None.
        - If the input is a valid integer, it returns the integer value.
        - If the
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
        
        This function tests the IntegerField with a minimum value of 10 and a maximum value of 20. It checks the rendering of the widget, validation of required fields, and the handling of values within the specified range. The function asserts that the widget renders correctly with the specified min and max attributes. It also verifies that the field raises a ValidationError for values outside the range and returns the correct values for valid inputs.
        
        Parameters:
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
        Test the clean method of the IntegerField class for handling large integer values.
        
        This function tests the clean method of the IntegerField class to ensure it correctly handles large integer values. The function checks the clean method with three different inputs: an integer, a string representation of the integer, and a string representation of the integer with a decimal point. The expected output for each case is the integer value 9223372036854775808.
        
        Parameters
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
    self.assertEqual(f.widget.__class__, Textarea)
qual(f.widget.__class__, Textarea)
