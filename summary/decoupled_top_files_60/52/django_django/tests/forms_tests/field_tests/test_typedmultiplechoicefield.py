import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedMultipleChoiceField
from django.test import SimpleTestCase


class TypedMultipleChoiceFieldTest(SimpleTestCase):

    def test_typedmultiplechoicefield_1(self):
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1], f.clean(['1']))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['2'])

    def test_typedmultiplechoicefield_2(self):
        """
        Tests the TypedMultipleChoiceField with a specific coercion function.
        
        This function tests the TypedMultipleChoiceField with a given set of choices and a coercion function. The field is expected to validate the input based on the provided choices and coerce the valid inputs using the specified function.
        
        Parameters:
        None (This function is a test case and does not take any parameters)
        
        Key Parameters:
        - choices: A list of tuples representing the choices for the field. Each tuple contains a value and a corresponding label.
        """

        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(['1']))

    def test_typedmultiplechoicefield_3(self):
        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertEqual([True], f.clean(['-1']))

    def test_typedmultiplechoicefield_4(self):
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1, -1], f.clean(['1', '-1']))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['1', '2'])

    def test_typedmultiplechoicefield_5(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with specific coercion and validation scenarios.
        
        This function tests the TypedMultipleChoiceField with a custom coercion function that converts choices to integers.
        It verifies that providing a valid choice but an invalid coercion results in a ValidationError, and that a required field
        without any input also raises a ValidationError.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the field validation does not behave as expected.
        
        Key Points:
        - Tests the field with choices ('
        """

        # Even more weirdness: if you have a valid choice but your coercion function
        # can't coerce, you'll still get a validation error. Don't do this!
        f = TypedMultipleChoiceField(choices=[('A', 'A'), ('B', 'B')], coerce=int)
        msg = "'Select a valid choice. B is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['B'])
        # Required fields require values
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])

    def test_typedmultiplechoicefield_6(self):
        """
        Tests the behavior of the TypedMultipleChoiceField when cleaning an empty list with a non-required field.
        This function creates an instance of TypedMultipleChoiceField with the following parameters:
        - choices: A list of tuples where each tuple contains an integer and a string representation.
        - coerce: A function to convert the input values to integers.
        - required: A boolean indicating that the field is not required.
        
        The function then calls the clean method on the field instance with an empty list as input and asserts that the
        """

        # Non-required fields aren't required
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False)
        self.assertEqual([], f.clean([]))

    def test_typedmultiplechoicefield_7(self):
        # If you want cleaning an empty value to return a different type, tell the field
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertIsNone(f.clean([]))

    def test_typedmultiplechoicefield_has_changed(self):
        """
        Tests the `has_changed` method for the `TypedMultipleChoiceField` class.
        
        This method checks if the `has_changed` method correctly identifies when the field has changed without triggering required validation. The `TypedMultipleChoiceField` is initialized with the following parameters:
        - `choices`: A list of tuples where each tuple contains a value and a display string. The choices are [(1, "+1"), (-1, "-1")].
        - `coerce`: A function to convert the input data
        """

        # has_changed should not trigger required validation
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=True)
        self.assertFalse(f.has_changed(None, ''))

    def test_typedmultiplechoicefield_special_coerce(self):
        """
        A coerce function which results in a value not present in choices
        should raise an appropriate error (#21397).
        """
        def coerce_func(val):
            return decimal.Decimal('1.%s' % val)

        f = TypedMultipleChoiceField(
            choices=[(1, "1"), (2, "2")], coerce=coerce_func, required=True)
        self.assertEqual([decimal.Decimal('1.2')], f.clean(['2']))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['3'])
