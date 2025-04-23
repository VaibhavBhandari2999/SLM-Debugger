import decimal

from django.forms import TypedMultipleChoiceField, ValidationError
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
        Tests the behavior of the TypedMultipleChoiceField with a specific coercion function.
        
        This test verifies that the TypedMultipleChoiceField correctly coerces input values to floats while maintaining the same validation logic as the default coercion.
        
        Parameters:
        - None (This test function does not take any parameters)
        
        Returns:
        - None (This test function does not return any value)
        
        Key Points:
        - The field is configured with choices for +1 and -1.
        - The coerce parameter is set to float, indicating that the input
        """

        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(['1']))

    def test_typedmultiplechoicefield_3(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with a boolean coercion.
        
        This test specifically checks how the field handles boolean values when they are coerced from integers. The field is configured with a list of choices, where each choice is an integer paired with a string representation. The coerce parameter is set to bool, which means the field will attempt to convert the input values to boolean. The test verifies that the field correctly interprets -1 as True, demonstrating the potential for unexpected behavior due to the boolean
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
        Tests the behavior of the TypedMultipleChoiceField with specific coercions and validation scenarios.
        
        This function tests the TypedMultipleChoiceField with a custom coercion function and verifies the following:
        - If a valid choice is provided but the coercion function cannot coerce it, a ValidationError is raised.
        - If the field is required and no value is provided, a ValidationError is raised.
        
        Parameters:
        - No external parameters are passed to this function. It is a test method for a Django form field.
        
        Returns:
        - None:
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
        # If you want cleaning an empty value to return a different type, tell the field
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertIsNone(f.clean([]))

    def test_typedmultiplechoicefield_has_changed(self):
        """
        Tests the `has_changed` method of the `TypedMultipleChoiceField` class.
        
        This method checks whether the `has_changed` method correctly identifies when the field has changed without triggering required validation. The `has_changed` method is called with two parameters: the initial value (`None`) and the current value (`''`), and it returns `False` in this case.
        
        Parameters:
        - f (TypedMultipleChoiceField): The TypedMultipleChoiceField instance to test.
        
        Returns:
        None:
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
