from django.core.exceptions import ValidationError
from django.forms import IntegerField, Textarea
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class IntegerFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_integerfield_1(self):
        """
        Tests the behavior of the IntegerField class.
        
        This function verifies that the IntegerField correctly handles integer
        inputs, renders the appropriate HTML widget, and raises validation errors
        for invalid or missing values. It checks the clean method for various
        input types and ensures that the cleaned value is an integer.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: Raised when the input is not a valid integer.
        
        Important Functions:
        - assertWidgetR
        """

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
        Tests the behavior of the IntegerField class from the Django forms framework.
        
        This function verifies that the IntegerField correctly handles various inputs,
        including empty strings, None values, valid integers, and invalid non-integer
        inputs. It also checks the clean method's ability to convert string representations
        of integers into actual integers and raises ValidationError for invalid inputs.
        
        Args:
        No explicit arguments are required as this is a test method.
        
        Returns:
        None: This function does not return
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
        Tests the behavior of an IntegerField with a maximum value constraint.
        
        - Validates the rendered widget includes the specified `max` attribute.
        - Ensures the field raises a `ValidationError` when no value is provided.
        - Confirms the field correctly converts integer values within the range [1, 10].
        - Verifies the field raises a `ValidationError` for values exceeding the maximum allowed value.
        - Checks the field handles string inputs appropriately.
        - Asserts the maximum value
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
        """
        Tests the behavior of an IntegerField with a specified minimum value.
        
        - Validates that the field renders correctly with a number input widget and a specified minimum value attribute.
        - Ensures that the field raises a ValidationError when no value is provided.
        - Verifies that the field raises a ValidationError when a value less than the specified minimum is provided.
        - Confirms that the field correctly returns the specified minimum value when cleaned with that value.
        - Checks that values greater than or equal to
        """

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
        """
        Tests the behavior of an IntegerField with specified min_value and max_value constraints. The field ensures that input values are within the range [10, 20], inclusive. It validates the input using a number input widget with min and max attributes set accordingly. The function checks the following:
        - Widget rendering
        - Required field validation
        - Minimum value validation
        - Maximum value validation
        - Conversion of string inputs to integers
        - Field's min_value and max_value
        """

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
        """
        Tests the behavior of the IntegerField with a specified step size.
        
        - Creates an IntegerField instance with a step size of 3.
        - Asserts that the widget renders correctly with the specified step size.
        - Validates that the clean method raises a ValidationError if the input is not a multiple of the step size.
        - Verifies that the clean method returns the correct integer values when valid inputs are provided.
        - Confirms that the step size attribute is set correctly.
        
        Args:
        """

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
        - IntegerField.clean: Cleans and validates the input value.
        - assertEqual: Compares expected and actual outputs.
        - assertRaisesMessage: Checks if a specific error message is raised.
        """

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
