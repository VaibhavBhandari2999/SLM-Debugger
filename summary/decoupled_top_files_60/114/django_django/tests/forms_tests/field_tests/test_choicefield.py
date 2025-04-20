from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):
    def test_choicefield_1(self):
        """
        Tests the behavior of a ChoiceField in Django forms.
        
        This function tests the validation and cleaning behavior of a ChoiceField with the following key parameters:
        - `f`: The ChoiceField instance with predefined choices.
        
        Key functionalities tested:
        - Raises a ValidationError with the message "'This field is required.'" when the input is empty or None.
        - Correctly returns the cleaned value when the input matches one of the choices.
        - Raises a ValidationError with a specific message when the input does not match any of the available
        """

        f = ChoiceField(choices=[("1", "One"), ("2", "Two")])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean("")
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual("1", f.clean(1))
        self.assertEqual("1", f.clean("1"))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("3")

    def test_choicefield_2(self):
        f = ChoiceField(choices=[("1", "One"), ("2", "Two")], required=False)
        self.assertEqual("", f.clean(""))
        self.assertEqual("", f.clean(None))
        self.assertEqual("1", f.clean(1))
        self.assertEqual("1", f.clean("1"))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("3")

    def test_choicefield_3(self):
        f = ChoiceField(choices=[("J", "John"), ("P", "Paul")])
        self.assertEqual("J", f.clean("J"))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("John")

    def test_choicefield_4(self):
        f = ChoiceField(
            choices=[
                ("Numbers", (("1", "One"), ("2", "Two"))),
                ("Letters", (("3", "A"), ("4", "B"))),
                ("5", "Other"),
            ]
        )
        self.assertEqual("1", f.clean(1))
        self.assertEqual("1", f.clean("1"))
        self.assertEqual("3", f.clean(3))
        self.assertEqual("3", f.clean("3"))
        self.assertEqual("5", f.clean(5))
        self.assertEqual("5", f.clean("5"))
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("6")

    def test_choicefield_choices_default(self):
        f = ChoiceField()
        self.assertEqual(f.choices, [])

    def test_choicefield_callable(self):
        """
        Tests the behavior of a ChoiceField with a callable choices function.
        
        This function creates a ChoiceField with a callable that returns a list of choices. The callable is expected to return a list of tuples, where each tuple contains a value and a display name. The function then cleans the input "J" and asserts that it returns "J".
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A ChoiceField is created using a callable that returns a list of choices.
        -
        """

        def choices():
            return [("J", "John"), ("P", "Paul")]

        f = ChoiceField(choices=choices)
        self.assertEqual("J", f.clean("J"))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
        choices = []

        def choices_as_callable():
            return choices

        class ChoiceFieldForm(Form):
            choicefield = ChoiceField(choices=choices_as_callable)

        choices = [("J", "John")]
        form = ChoiceFieldForm()
        self.assertEqual([("J", "John")], list(form.fields["choicefield"].choices))

        choices = [("P", "Paul")]
        form = ChoiceFieldForm()
        self.assertEqual([("P", "Paul")], list(form.fields["choicefield"].choices))

    def test_choicefield_disabled(self):
        f = ChoiceField(choices=[("J", "John"), ("P", "Paul")], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>',
        )

    def test_choicefield_enumeration(self):
        """
        Tests the functionality of a ChoiceField with enumerated choices.
        
        This function tests a ChoiceField that uses a custom enumeration defined by the FirstNames TextChoices class. The test covers the following aspects:
        - Ensuring the ChoiceField's choices match the defined enumeration.
        - Validating that the field correctly cleans and returns the expected value for a valid choice.
        - Verifying that the field raises a ValidationError for an invalid choice.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The ChoiceField
        """

        class FirstNames(models.TextChoices):
            JOHN = "J", "John"
            PAUL = "P", "Paul"

        f = ChoiceField(choices=FirstNames)
        self.assertEqual(f.choices, FirstNames.choices)
        self.assertEqual(f.clean("J"), "J")
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("3")
