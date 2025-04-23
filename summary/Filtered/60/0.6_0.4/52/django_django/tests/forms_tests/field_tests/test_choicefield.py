from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')

    def test_choicefield_2(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')

    def test_choicefield_3(self):
        """
        Tests the behavior of a ChoiceField in a Django form.
        
        This function tests the clean method of a ChoiceField with the following key parameters:
        - `f`: A ChoiceField instance with choices for 'J' (John) and 'P' (Paul).
        
        The function performs the following actions:
        1. Validates that the clean method returns 'J' when 'J' is passed as input.
        2. Checks that a ValidationError is raised with a specific error message when an invalid choice ('John') is
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual('J', f.clean('J'))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('John')

    def test_choicefield_4(self):
        f = ChoiceField(
            choices=[
                ('Numbers', (('1', 'One'), ('2', 'Two'))),
                ('Letters', (('3', 'A'), ('4', 'B'))), ('5', 'Other'),
            ]
        )
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        self.assertEqual('3', f.clean(3))
        self.assertEqual('3', f.clean('3'))
        self.assertEqual('5', f.clean(5))
        self.assertEqual('5', f.clean('5'))
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('6')

    def test_choicefield_choices_default(self):
        f = ChoiceField()
        self.assertEqual(f.choices, [])

    def test_choicefield_callable(self):
        """
        Tests the behavior of a ChoiceField with a callable choices function.
        
        This function creates a ChoiceField with a callable that returns a list of choices.
        The callable is expected to return a list of tuples, where each tuple contains a value and a display name.
        The function then cleans the field with a valid input and asserts that the cleaned value matches the input.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A ChoiceField is created with a callable that returns a list of choices
        """

        def choices():
            return [('J', 'John'), ('P', 'Paul')]
        f = ChoiceField(choices=choices)
        self.assertEqual('J', f.clean('J'))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
        """
        Tests the behavior of a ChoiceField when its choices are provided by a callable function that may return different values each time it is called.
        
        Key Parameters:
        - choices: A list of choices to be set for the test.
        
        Keyword Parameters:
        - choices_as_callable: A callable function that returns a list of choices.
        
        Output:
        - The function asserts that the choices returned by the callable are correctly evaluated and displayed in the ChoiceField.
        
        Test Steps:
        1. Define a callable function `choices_as_callable` that
        """

        choices = []

        def choices_as_callable():
            return choices

        class ChoiceFieldForm(Form):
            choicefield = ChoiceField(choices=choices_as_callable)

        choices = [('J', 'John')]
        form = ChoiceFieldForm()
        self.assertEqual([('J', 'John')], list(form.fields['choicefield'].choices))

        choices = [('P', 'Paul')]
        form = ChoiceFieldForm()
        self.assertEqual([('P', 'Paul')], list(form.fields['choicefield'].choices))

    def test_choicefield_disabled(self):
        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_choicefield_enumeration(self):
        """
        Tests the behavior of a ChoiceField with a custom enumeration.
        
        This function tests the `clean` method of a Django `ChoiceField` that uses a custom enumeration defined in `FirstNames`. The `clean` method should correctly validate the input against the available choices and raise a `ValidationError` if an invalid choice is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `FirstNames` enumeration is defined with two choices: 'J' for 'John' and '
        """

        class FirstNames(models.TextChoices):
            JOHN = 'J', 'John'
            PAUL = 'P', 'Paul'

        f = ChoiceField(choices=FirstNames.choices)
        self.assertEqual(f.clean('J'), 'J')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
