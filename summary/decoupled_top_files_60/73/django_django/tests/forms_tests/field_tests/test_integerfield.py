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
        Tests the clean method of the IntegerField class.
        
        This function tests the clean method of the IntegerField class, which is responsible for validating and converting input to an integer. The method is tested with various inputs, including empty strings, None, valid integers, invalid integers, and integers with leading/trailing spaces. The function also verifies that the method handles max_value and min_value constraints, although these are not explicitly set in the test.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Tests:
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
        """
        Test the IntegerField with specified min_value.
        
        This test function checks the behavior of the IntegerField with a minimum value constraint. The field is configured to accept integers greater than or equal to 10. The function tests the rendering of the widget, validation of required fields, and the handling of valid and invalid input values.
        
        Parameters:
        - None (The function uses internal assertions and does not take any parameters).
        
        Returns:
        - None (The function asserts expected outcomes and does not return any value).
        
        Key
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
        
        This function verifies that the IntegerField class correctly handles various inputs and raises a ValidationError for non-integer values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Verifications:
        - The function checks that 1.0, '1.0', ' 1.0 ', '1.', and ' 1. ' are all cleaned to 1.
        - It ensures that '1.5' and '…' raise a ValidationError with
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
        Tests the clean method of the IntegerField for handling large integer values.
        
        This function verifies that the IntegerField correctly processes and returns large integer values, including those provided as integers, strings, and floating-point numbers with no decimal places.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the IntegerField's clean method to validate large integer values.
        - It checks that the clean method returns the expected integer value for different input types.
        - The test includes a
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
tEqual(f.widget.__class__, Textarea)
