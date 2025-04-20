from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        """
        Tests the behavior of a ChoiceField in a Django form.
        
        This function tests the validation and cleaning methods of a ChoiceField with the following key parameters:
        - `f`: The ChoiceField instance to be tested.
        - `choices`: A list of tuples representing the choices available in the ChoiceField.
        
        The function performs the following tests:
        1. Validates that an empty string raises a ValidationError with the message "'This field is required.'".
        2. Validates that None raises a ValidationError with the message "'This field
        """

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
        - `f`: A ChoiceField instance with choices set to [('J', 'John'), ('P', 'Paul')].
        
        The function performs the following actions:
        1. Validates that the clean method returns 'J' when 'J' is passed as input.
        2. Validates that a ValidationError is raised with the specific error message "'Select a valid choice. John
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
        def choices():
            return [('J', 'John'), ('P', 'Paul')]
        f = ChoiceField(choices=choices)
        self.assertEqual('J', f.clean('J'))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
        """
        Tests that a callable used for choices in a ChoiceField may evaluate to different values depending on when it is called.
        
        This function creates a form with a ChoiceField that uses a callable for its choices. The callable returns a list of choices, which can be modified between calls to the form.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key behaviors:
        - The form is instantiated with different choices each time, demonstrating that the callable is evaluated at each instantiation.
        - The choices for the 'choicefield
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
        """
        Test the rendering of a disabled ChoiceField.
        
        This function checks if a ChoiceField with specified choices and a disabled attribute is rendered correctly. The field is expected to have its options displayed with the 'disabled' attribute applied to the select element.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - choices: A list of tuples where each tuple contains a value and a display name for the option.
        - disabled: A boolean indicating if the field should be disabled.
        
        Expected Output:
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_choicefield_enumeration(self):
        """
        Tests the behavior of a ChoiceField with an enumeration of first names.
        
        This function creates a ChoiceField using a custom enumeration of first names and tests its validation behavior.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a custom enumeration `FirstNames` with two choices: 'J' for 'John' and 'P' for 'Paul'.
        - A ChoiceField is instantiated with these choices.
        - The function tests the `clean` method of the ChoiceField:
        """

        class FirstNames(models.TextChoices):
            JOHN = 'J', 'John'
            PAUL = 'P', 'Paul'

        f = ChoiceField(choices=FirstNames.choices)
        self.assertEqual(f.clean('J'), 'J')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
