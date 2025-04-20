from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        """
        Tests the behavior of a ChoiceField in a form.
        
        This function tests the validation and cleaning behavior of a ChoiceField with the following key parameters:
        - `choices`: A list of tuples where each tuple contains a value and a display name for the choices.
        
        The function performs the following tests:
        1. Validates that an empty string raises a ValidationError with the message "'This field is required.'".
        2. Validates that None raises a ValidationError with the message "'This field is required.'".
        3. Validates that
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
        
        This function tests the clean method of a ChoiceField with predefined choices. It verifies that the field correctly returns the selected value when a valid choice is provided and raises a ValidationError with a specific error message when an invalid choice is provided.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None
        
        Key Parameters:
        - f: The ChoiceField instance with predefined choices.
        
        Key Keywords:
        - choices: A list
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual('J', f.clean('J'))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('John')

    def test_choicefield_4(self):
        """
        Tests the behavior of a ChoiceField with nested choices.
        
        This function tests the `clean` method of a Django `ChoiceField` with nested choices. The field is configured with a list of choices, where some choices are nested in tuples. The test verifies that the field correctly maps input values to the corresponding choices and raises a `ValidationError` for invalid inputs.
        
        Parameters:
        - None (The function uses internal parameters defined in the test case context)
        
        Returns:
        - None (The function asserts expected outcomes and
        """

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
        Tests the behavior of a ChoiceField when its choices are provided as a callable function that may return different values each time it is called.
        
        Key Parameters:
        - choices: A list of tuples representing the initial choices for the ChoiceField.
        
        Keyword Arguments:
        - choices_as_callable: A callable function that returns the choices for the ChoiceField.
        
        Output:
        - None. The function asserts the expected behavior of the ChoiceField by checking the choices after setting them to different values.
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
        class FirstNames(models.TextChoices):
            JOHN = 'J', 'John'
            PAUL = 'P', 'Paul'

        f = ChoiceField(choices=FirstNames.choices)
        self.assertEqual(f.clean('J'), 'J')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
