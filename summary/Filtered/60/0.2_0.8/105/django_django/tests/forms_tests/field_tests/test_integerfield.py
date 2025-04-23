from django.core.exceptions import ValidationError
from django.forms import IntegerField, Textarea
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class IntegerFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_integerfield_1(self):
        f = IntegerField()
        self.assertWidgetRendersTo(
            f, '<input type="number" name="f" id="id_f" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1, f.clean("1"))
        self.assertIsInstance(f.clean("1"), int)
        self.assertEqual(23, f.clean("23"))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("a")
        self.assertEqual(42, f.clean(42))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean(3.14)
        self.assertEqual(1, f.clean("1 "))
        self.assertEqual(1, f.clean(" 1"))
        self.assertEqual(1, f.clean(" 1 "))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("1a")
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_integerfield_2(self):
        """
        Tests the behavior of the IntegerField in a form.
        
        This function tests the IntegerField to ensure it correctly handles various inputs and edge cases. The field is configured to be optional (required=False).
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Tests:
        - Validates that an empty string and None are cleaned to None.
        - Confirms that valid integers are cleaned and returned as integers.
        - Ensures that non-integer strings raise a ValidationError with the message 'Enter a whole number.'.
        -
        """

        f = IntegerField(required=False)
        self.assertIsNone(f.clean(""))
        self.assertEqual("None", repr(f.clean("")))
        self.assertIsNone(f.clean(None))
        self.assertEqual("None", repr(f.clean(None)))
        self.assertEqual(1, f.clean("1"))
        self.assertIsInstance(f.clean("1"), int)
        self.assertEqual(23, f.clean("23"))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("a")
        self.assertEqual(1, f.clean("1 "))
        self.assertEqual(1, f.clean(" 1"))
        self.assertEqual(1, f.clean(" 1 "))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("1a")
        self.assertIsNone(f.max_value)
        self.assertIsNone(f.min_value)

    def test_integerfield_3(self):
        """
        Tests the behavior of the IntegerField with a maximum value constraint.
        
        This function tests the IntegerField with a maximum value of 10. It checks the rendering of the widget, validation of clean method, and the max_value attribute.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Widget Rendering: The widget is expected to render with a maximum value of 10.
        - Validation: The clean method should validate integer inputs and raise ValidationError for values greater than 10.
        """

        f = IntegerField(max_value=10)
        self.assertWidgetRendersTo(
            f, '<input max="10" type="number" name="f" id="id_f" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(1, f.clean(1))
        self.assertEqual(10, f.clean(10))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is less than or equal to 10.'"
        ):
            f.clean(11)
        self.assertEqual(10, f.clean("10"))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is less than or equal to 10.'"
        ):
            f.clean("11")
        self.assertEqual(f.max_value, 10)
        self.assertIsNone(f.min_value)

    def test_integerfield_4(self):
        f = IntegerField(min_value=10)
        self.assertWidgetRendersTo(
            f, '<input id="id_f" type="number" name="f" min="10" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is greater than or equal to 10.'"
        ):
            f.clean(1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean("10"))
        self.assertEqual(11, f.clean("11"))
        self.assertIsNone(f.max_value)
        self.assertEqual(f.min_value, 10)

    def test_integerfield_5(self):
        f = IntegerField(min_value=10, max_value=20)
        self.assertWidgetRendersTo(
            f, '<input id="id_f" max="20" type="number" name="f" min="10" required>'
        )
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is greater than or equal to 10.'"
        ):
            f.clean(1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean("10"))
        self.assertEqual(11, f.clean("11"))
        self.assertEqual(20, f.clean(20))
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is less than or equal to 20.'"
        ):
            f.clean(21)
        self.assertEqual(f.max_value, 20)
        self.assertEqual(f.min_value, 10)

    def test_integerfield_6(self):
        f = IntegerField(step_size=3)
        self.assertWidgetRendersTo(
            f,
            '<input name="f" step="3" type="number" id="id_f" required>',
        )
        with self.assertRaisesMessage(
            ValidationError, "'Ensure this value is a multiple of step size 3.'"
        ):
            f.clean("10")
        self.assertEqual(12, f.clean(12))
        self.assertEqual(12, f.clean("12"))
        self.assertEqual(f.step_size, 3)

    def test_integerfield_localized(self):
        """
        A localized IntegerField's widget renders to a text input without any
        number input specific attributes.
        """
        f1 = IntegerField(localize=True)
        self.assertWidgetRendersTo(
            f1, '<input id="id_f" name="f" type="text" required>'
        )

    def test_integerfield_float(self):
        f = IntegerField()
        self.assertEqual(1, f.clean(1.0))
        self.assertEqual(1, f.clean("1.0"))
        self.assertEqual(1, f.clean(" 1.0 "))
        self.assertEqual(1, f.clean("1."))
        self.assertEqual(1, f.clean(" 1. "))
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("1.5")
        with self.assertRaisesMessage(ValidationError, "'Enter a whole number.'"):
            f.clean("…")

    def test_integerfield_big_num(self):
        f = IntegerField()
        self.assertEqual(9223372036854775808, f.clean(9223372036854775808))
        self.assertEqual(9223372036854775808, f.clean("9223372036854775808"))
        self.assertEqual(9223372036854775808, f.clean("9223372036854775808.0"))

    def test_integerfield_unicode_number(self):
        f = IntegerField()
        self.assertEqual(50, f.clean("５０"))

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
