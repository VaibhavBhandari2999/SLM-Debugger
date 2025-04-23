import decimal

from django.core.exceptions import ValidationError
from django.forms import TypedMultipleChoiceField
from django.test import SimpleTestCase


class TypedMultipleChoiceFieldTest(SimpleTestCase):
    def test_typedmultiplechoicefield_1(self):
        """
        Tests the behavior of the TypedMultipleChoiceField with integer coercion.
        
        This function tests the TypedMultipleChoiceField to ensure it correctly coerces input values to integers and validates them against the provided choices.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `f`: An instance of TypedMultipleChoiceField configured to accept choices from the list [(1, "+1"), (-1, "-1")] and coerce input values to integers.
        
        Key Keywords:
        - `choices`: A list
        """

        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual([1], f.clean(["1"]))
        msg = "'Select a valid choice. 2 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["2"])

    def test_typedmultiplechoicefield_2(self):
        # Different coercion, same validation.
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual([1.0], f.clean(["1"]))

    def test_typedmultiplechoicefield_3(self):
        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedMultipleChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertEqual([True], f.clean(["-1"]))

    def test_typedmultiplechoicefield_4(self):
        """
        Tests the `TypedMultipleChoiceField` with specific choices and coercion.
        
        This function tests the `TypedMultipleChoiceField` with a list of choices and a coercion function. It verifies that the field correctly converts the input values to integers and raises a `ValidationError` if an invalid choice is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `choices`: A list of tuples representing the choices. Each tuple contains a value and a display text.
        - `coerce
        """

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
        
        This method checks if the `has_changed` method correctly identifies when the field has changed without triggering required validation. The field is initialized with integer-coerced choices and is marked as required.
        
        Parameters:
        - `f`: The `TypedMultipleChoiceField` instance to test.
        
        Returns:
        - `bool`: `False` if the field has not changed and no required validation was triggered, otherwise `True`.
        
        Key Parameters
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
