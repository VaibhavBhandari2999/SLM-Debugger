import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedMultipleChoiceField
from django.test import SimpleTestCase


class TypedMultipleChoiceFieldTest(SimpleTestCase):

    def test_typedmultiplechoicefield_1(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with integer coercion.
        
        This function creates an instance of TypedMultipleChoiceField with choices for +1 and -1, and specifies that the input values should be coerced to integers. It then tests the clean method to ensure that it correctly converts the input '1' to an integer [1] and raises a ValidationError with the appropriate message when an invalid choice '2' is provided.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValidationError
        """

        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1], f.clean(['1']))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['2'])

    def test_typedmultiplechoicefield_2(self):
        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(['1']))

    def test_typedmultiplechoicefield_3(self):
        """
        Tests the behavior of the TypedMultipleChoiceField when given a list of choices that include boolean values. The field is configured to coerce the input values to boolean. The test verifies that the field correctly interprets the string '-1' as False, even though -1 is truthy in Python.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The field is defined with choices for 1 and -1, with corresponding labels '+1' and '-1'.
        - The coerce parameter
        """

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
        Tests the behavior of the TypedMultipleChoiceField with specific coercions and validation.
        
        This function tests the TypedMultipleChoiceField with a list of valid choices and a coercion function that converts the choices to integers. It checks the following scenarios:
        1. Validates that an invalid choice (B) raises a ValidationError with a specific error message.
        2. Validates that a required field without any input raises a ValidationError with a specific error message.
        
        Parameters:
        - No external parameters are passed to this function. It uses internal
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
        # Non-required fields aren't required
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False)
        self.assertEqual([], f.clean([]))

    def test_typedmultiplechoicefield_7(self):
        """
        Tests the behavior of the TypedMultipleChoiceField when cleaning an empty value.
        
        This function creates an instance of the TypedMultipleChoiceField with specific parameters:
        - `choices`: A list of tuples where each tuple contains a value and a display string. The choices are [(1, "+1"), (-1, "-1")].
        - `coerce`: A function to convert the input value to the desired type, in this case, `int`.
        - `required`: A boolean indicating whether the field is
        """

        # If you want cleaning an empty value to return a different type, tell the field
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertIsNone(f.clean([]))

    def test_typedmultiplechoicefield_has_changed(self):
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
