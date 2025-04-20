from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField
from django.test import SimpleTestCase


class MultipleChoiceFieldTest(SimpleTestCase):
    def test_multiplechoicefield_1(self):
        """
        Tests the behavior of the MultipleChoiceField.
        
        This function tests the validation and cleaning of a MultipleChoiceField with the following key parameters:
        - `f`: The MultipleChoiceField instance with predefined choices.
        
        Key functionalities tested:
        - Validation of empty and `None` inputs.
        - Correct handling of valid list inputs.
        - Error handling for invalid inputs, including non-list types and invalid choices.
        
        Returns:
        - None: The function asserts expected behavior through validation messages.
        
        Raises:
        - ValidationError: When the input does
        """

        f = MultipleChoiceField(choices=[("1", "One"), ("2", "Two")])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(["1"], f.clean([1]))
        self.assertEqual(["1"], f.clean(["1"]))
        self.assertEqual(["1", "2"], f.clean(["1", "2"]))
        self.assertEqual(["1", "2"], f.clean([1, "2"]))
        self.assertEqual(["1", "2"], f.clean((1, "2")))
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean("hello")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(())
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["3"])

    def test_multiplechoicefield_2(self):
        f = MultipleChoiceField(choices=[("1", "One"), ("2", "Two")], required=False)
        self.assertEqual([], f.clean(""))
        self.assertEqual([], f.clean(None))
        self.assertEqual(["1"], f.clean([1]))
        self.assertEqual(["1"], f.clean(["1"]))
        self.assertEqual(["1", "2"], f.clean(["1", "2"]))
        self.assertEqual(["1", "2"], f.clean([1, "2"]))
        self.assertEqual(["1", "2"], f.clean((1, "2")))
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean("hello")
        self.assertEqual([], f.clean([]))
        self.assertEqual([], f.clean(()))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["3"])

    def test_multiplechoicefield_3(self):
        f = MultipleChoiceField(
            choices=[
                ("Numbers", (("1", "One"), ("2", "Two"))),
                ("Letters", (("3", "A"), ("4", "B"))),
                ("5", "Other"),
            ]
        )
        self.assertEqual(["1"], f.clean([1]))
        self.assertEqual(["1"], f.clean(["1"]))
        self.assertEqual(["1", "5"], f.clean([1, 5]))
        self.assertEqual(["1", "5"], f.clean([1, "5"]))
        self.assertEqual(["1", "5"], f.clean(["1", 5]))
        self.assertEqual(["1", "5"], f.clean(["1", "5"]))
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["6"])
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(["1", "6"])

    def test_multiplechoicefield_changed(self):
        """
        Tests the behavior of the MultipleChoiceField's has_changed method.
        
        This method checks if the state of the field has changed between two sets of values. It takes no parameters and does not return any value. Instead, it asserts the expected behavior of the has_changed method for different input scenarios.
        
        Key Assertions:
        - The field has not changed when both old and new values are None.
        - The field has not changed when the new value is an empty list.
        - The field has changed when the new value
        """

        f = MultipleChoiceField(choices=[("1", "One"), ("2", "Two"), ("3", "Three")])
        self.assertFalse(f.has_changed(None, None))
        self.assertFalse(f.has_changed([], None))
        self.assertTrue(f.has_changed(None, ["1"]))
        self.assertFalse(f.has_changed([1, 2], ["1", "2"]))
        self.assertFalse(f.has_changed([2, 1], ["1", "2"]))
        self.assertTrue(f.has_changed([1, 2], ["1"]))
        self.assertTrue(f.has_changed([1, 2], ["1", "3"]))

    def test_disabled_has_changed(self):
        f = MultipleChoiceField(choices=[("1", "One"), ("2", "Two")], disabled=True)
        self.assertIs(f.has_changed("x", "y"), False)
