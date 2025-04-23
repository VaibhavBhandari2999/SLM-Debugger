import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedChoiceField
from django.test import SimpleTestCase


class TypedChoiceFieldTest(SimpleTestCase):

    def test_typedchoicefield_1(self):
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
        Test the behavior of the TypedChoiceField with boolean coercion.
        
        This test case checks how the TypedChoiceField handles boolean coercion with choices that include integer values. Specifically, it tests whether the field correctly interprets the string '-1' as the boolean value False when the coerce parameter is set to bool. The choices are provided as a list of tuples, where each tuple contains an integer and its corresponding string representation.
        
        Parameters:
        - No explicit parameters are passed in the function. Instead, the field is defined
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
        """
        Tests the behavior of the `has_changed` method for a `TypedChoiceField`.
        
        The `has_changed` method is used to determine if the field's value has changed
        between two states. This method should not trigger required validation when
        checking for changes.
        
        Parameters:
        - `f`: A `TypedChoiceField` instance with specified choices, coercion, and required status.
        
        Returns:
        - `None`: The function does not return any value but asserts the behavior of the `has_changed` method.
        """

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
