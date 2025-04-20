import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedChoiceField
from django.test import SimpleTestCase


class TypedChoiceFieldTest(SimpleTestCase):

    def test_typedchoicefield_1(self):
        """
        Tests the behavior of the TypedChoiceField with integer choices.
        
        This function creates an instance of TypedChoiceField with choices for +1 and -1, and the coerce parameter set to int. It then tests the clean method to ensure that it correctly converts the string '1' to the integer 1 and raises a ValidationError with the appropriate message when an invalid choice '2' is provided.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: If the input '2' is
        """

        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual(1, f.clean('1'))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('2')

    def test_typedchoicefield_2(self):
        # Different coercion, same validation.
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual(1.0, f.clean('1'))

    def test_typedchoicefield_3(self):
        """
        Tests the behavior of the TypedChoiceField with boolean coercion.
        
        This function creates a TypedChoiceField with choices for +1 and -1, and a coerce function that converts the input to a boolean. It then tests the clean method to ensure that the string '-1' is correctly converted to True.
        
        Parameters:
        - None (This function uses internal parameters defined in the test case context)
        
        Returns:
        - None (This function asserts the correctness of the TypedChoiceField behavior, no explicit return value
        
        Key
        """

        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertTrue(f.clean('-1'))

    def test_typedchoicefield_4(self):
        # Even more weirdness: if you have a valid choice but your coercion function
        # can't coerce, you'll still get a validation error. Don't do this!
        f = TypedChoiceField(choices=[('A', 'A'), ('B', 'B')], coerce=int)
        msg = "'Select a valid choice. B is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('B')
        # Required fields require values
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')

    def test_typedchoicefield_5(self):
        # Non-required fields aren't required
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False)
        self.assertEqual('', f.clean(''))
        # If you want cleaning an empty value to return a different type, tell the field

    def test_typedchoicefield_6(self):
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertIsNone(f.clean(''))

    def test_typedchoicefield_has_changed(self):
        # has_changed should not trigger required validation
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=True)
        self.assertFalse(f.has_changed(None, ''))
        self.assertFalse(f.has_changed(1, '1'))
        self.assertFalse(f.has_changed('1', '1'))

        f = TypedChoiceField(
            choices=[('', '---------'), ('a', "a"), ('b', "b")], coerce=str,
            required=False, initial=None, empty_value=None,
        )
        self.assertFalse(f.has_changed(None, ''))
        self.assertTrue(f.has_changed('', 'a'))
        self.assertFalse(f.has_changed('a', 'a'))

    def test_typedchoicefield_special_coerce(self):
        """
        A coerce function which results in a value not present in choices
        should raise an appropriate error (#21397).
        """
        def coerce_func(val):
            return decimal.Decimal('1.%s' % val)

        f = TypedChoiceField(choices=[(1, "1"), (2, "2")], coerce=coerce_func, required=True)
        self.assertEqual(decimal.Decimal('1.2'), f.clean('2'))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
