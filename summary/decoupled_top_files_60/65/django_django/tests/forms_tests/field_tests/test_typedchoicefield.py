import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedChoiceField
from django.test import SimpleTestCase


class TypedChoiceFieldTest(SimpleTestCase):

    def test_typedchoicefield_1(self):
        """
        Tests the TypedChoiceField with integer choices.
        
        This function tests the `TypedChoiceField` with a list of integer choices. The field is initialized with two choices: 1 and -1, each represented as a string. The `coerce` parameter is set to `int`, meaning the input values will be converted to integers during validation.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError: If the input value is not one of the available choices after coercion.
        
        Example usage
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
        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertTrue(f.clean('-1'))

    def test_typedchoicefield_4(self):
        """
        Tests the behavior of the TypedChoiceField in Django forms.
        
        This function tests the TypedChoiceField with a custom coercion function. It verifies that:
        1. A validation error is raised when an invalid choice is provided, even if the coercion function cannot handle the choice.
        2. A validation error is raised when the field is required and no value is provided.
        
        Key Parameters:
        - `choices`: A list of tuples representing the choices for the field. Each tuple contains a value and a display name.
        -
        """

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
        Tests the `has_changed` method of the `TypedChoiceField` class.
        
        This method checks whether the `has_changed` method of the `TypedChoiceField` class behaves correctly under different conditions. It ensures that the method does not trigger required validation and correctly identifies changes in the field's value.
        
        Parameters:
        - `f`: The `TypedChoiceField` instance being tested.
        
        Key Parameters:
        - `f`: The `TypedChoiceField` instance to test.
        
        Key Keywords:
        - `choices`:
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
