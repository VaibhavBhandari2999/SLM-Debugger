import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedMultipleChoiceField
from django.test import SimpleTestCase


class TypedMultipleChoiceFieldTest(SimpleTestCase):
    def test_typedmultiplechoicefield_1(self):
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1], f.clean(["1"]))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["2"])

    def test_typedmultiplechoicefield_2(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with a specific coercion function.
        
        This function verifies that the TypedMultipleChoiceField correctly coerces input values to floats while maintaining the same validation logic as the default integer coercion.
        
        Parameters:
        None (This is a test function and does not take any parameters).
        
        Returns:
        None (This function is used for testing and does not return any value).
        
        Key Points:
        - The field uses a list of choices with integer values and their string representations.
        - The '
        """

        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(["1"]))

    def test_typedmultiplechoicefield_3(self):
        """
        Tests the behavior of the TypedMultipleChoiceField when coerced to a boolean.
        
        This function tests the TypedMultipleChoiceField with a list of choices that includes both a positive and negative integer. The field is configured to coerce the input values to boolean. The test case specifically checks the behavior when the input is a list containing the string representation of the negative integer '-1', which should be coerced to True.
        
        Parameters:
        - None (This is a test function and does not take any parameters).
        
        Returns
        """

        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertEqual([True], f.clean(["-1"]))

    def test_typedmultiplechoicefield_4(self):
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1, -1], f.clean(["1", "-1"]))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["1", "2"])

    def test_typedmultiplechoicefield_5(self):
        # Even more weirdness: if you have a valid choice but your coercion function
        # can't coerce, you'll still get a validation error. Don't do this!
        f = TypedMultipleChoiceField(choices=[("A", "A"), ("B", "B")], coerce=int)
        msg = "'Select a valid choice. B is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["B"])
        # Required fields require values
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])

    def test_typedmultiplechoicefield_6(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with an empty list input when the field is not required.
        This function creates a TypedMultipleChoiceField with the following parameters:
        - choices: A list of tuples where each tuple contains an integer and a string representation of the integer.
        - coerce: A function to convert the input to integers.
        - required: A boolean indicating that the field is not required.
        
        The function then calls the clean method of the field with an empty list as input and asserts that the
        """

        # Non-required fields aren't required
        f = TypedMultipleChoiceField(
            choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False
        )
        self.assertEqual([], f.clean([]))

    def test_typedmultiplechoicefield_7(self):
        # If you want cleaning an empty value to return a different type, tell the field
        f = TypedMultipleChoiceField(
            choices=[(1, "+1"), (-1, "-1")],
            coerce=int,
            required=False,
            empty_value=None,
        )
        self.assertIsNone(f.clean([]))

    def test_typedmultiplechoicefield_has_changed(self):
        """
        Tests the `has_changed` method of the `TypedMultipleChoiceField` class.
        
        This method checks if the `has_changed` method of the `TypedMultipleChoiceField` class correctly identifies when the field has changed without triggering required validation. The method takes no input parameters and does not return any value. It uses a `TypedMultipleChoiceField` with specific choices and coercion, and verifies that the field reports no change when transitioning from `None` to an empty string.
        
        Parameters:
        - None
        """

        # has_changed should not trigger required validation
        f = TypedMultipleChoiceField(
            choices=[(1, "+1"), (-1, "-1")], coerce=int, required=True
        )
        self.assertFalse(f.has_changed(None, ""))

    def test_typedmultiplechoicefield_special_coerce(self):
        """
        A coerce function which results in a value not present in choices
        should raise an appropriate error (#21397).
        """

        def coerce_func(val):
            return decimal.Decimal("1.%s" % val)

        f = TypedMultipleChoiceField(
            choices=[(1, "1"), (2, "2")], coerce=coerce_func, required=True
        )
        self.assertEqual([decimal.Decimal("1.2")], f.clean(["2"]))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["3"])
r, msg):
            f.clean(["3"])
