import decimal

from django.forms import TypedMultipleChoiceField, ValidationError
from django.test import SimpleTestCase


class TypedMultipleChoiceFieldTest(SimpleTestCase):

    def test_typedmultiplechoicefield_1(self):
        """
        Tests the `TypedMultipleChoiceField` with integer coercion.
        
        - **Parameters:**
        - `choices`: A list of tuples representing the available choices, where each tuple contains an integer and its corresponding string representation.
        - `coerce`: A function that converts the selected values to integers.
        
        - **Returns:**
        - `None`
        
        - **Assertions:**
        - Validates that the field correctly coerces and validates integer inputs.
        - Ensures that non-integer inputs
        """

        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1], f.clean(['1']))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['2'])

    def test_typedmultiplechoicefield_2(self):
        """
        Tests the `TypedMultipleChoiceField` with different coercion while ensuring the same validation.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `TypedMultipleChoiceField`: Creates a typed multiple choice field with specified choices and coercion.
        - `clean`: Cleans and validates the input data according to the field's rules.
        
        Input Variables:
        - No direct input variables.
        
        Output Variables:
        - The cleaned and validated result of the input data, in this
        """

        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(['1']))

    def test_typedmultiplechoicefield_3(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with boolean coercion.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        - Tests the TypedMultipleChoiceField with boolean coercion.
        - The field accepts choices [(1, "+1"), (-1, "-1")].
        - The clean method is called with ['-1'] as input.
        - The expected output is [True].
        """

        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertEqual([True], f.clean(['-1']))

    def test_typedmultiplechoicefield_4(self):
        """
        Tests the `TypedMultipleChoiceField` with integer coercion.
        
        This function verifies that the `TypedMultipleChoiceField` correctly handles
        integer values and raises a `ValidationError` when an invalid choice is
        provided.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `TypedMultipleChoiceField`: The field being tested, which coerces
        input choices into integers.
        - `clean`: Method called to validate and clean the input data.
        """

        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1, -1], f.clean(['1', '-1']))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['1', '2'])

    def test_typedmultiplechoicefield_5(self):
        """
        Tests the behavior of the TypedMultipleChoiceField when given invalid inputs or no values.
        
        This function verifies that the TypedMultipleChoiceField raises appropriate validation errors when:
        - A non-existent choice is selected (e.g., 'B' when choices are ['A', 'B']).
        - No value is provided (i.e., an empty list).
        
        Important Functions:
        - `TypedMultipleChoiceField`: The field being tested.
        - `clean`: Method used to validate and clean
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
        Tests the behavior of the TypedMultipleChoiceField with an empty list input when the field is not required. The field has choices defined as tuples of integers and their corresponding string representations, and uses the `int` type for coercion. When an empty list is passed to the clean method, it returns an empty list.
        """

        # Non-required fields aren't required
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False)
        self.assertEqual([], f.clean([]))

    def test_typedmultiplechoicefield_7(self):
        """
        Tests the behavior of the `TypedMultipleChoiceField` when cleaning an empty value. The field is configured to coerce choices into integers and does not require a value. Cleaning an empty list returns `None`.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `TypedMultipleChoiceField`: Configures the multiple choice field to handle typed choices.
        - `coerce=int`: Converts the selected choices to integers.
        - `required=False`: Indicates that the field
        """

        # If you want cleaning an empty value to return a different type, tell the field
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertIsNone(f.clean([]))

    def test_typedmultiplechoicefield_has_changed(self):
        """
        Tests whether the `has_changed` method of a TypedMultipleChoiceField does not trigger required validation when called with `None` and an empty string as arguments. The method uses a field configuration with choices, coercion, and a required flag set to True.
        
        Args:
        None (NoneType): The initial value passed to the `has_changed` method.
        '' (str): The current value passed to the `has_changed` method.
        
        Returns:
        bool: False, indicating that the
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
