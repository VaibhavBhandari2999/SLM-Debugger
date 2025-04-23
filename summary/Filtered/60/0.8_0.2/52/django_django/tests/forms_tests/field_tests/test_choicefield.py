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
        """
        Tests the behavior of a ChoiceField with specific choices and validation rules.
        
        This function tests the `clean` method of a `ChoiceField` instance with the following characteristics:
        - Choices: [('1', 'One'), ('2', 'Two')]
        - Required: False
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Returns:
        - None
        
        Test Cases:
        - Validates that an empty string or None is cleaned to an empty string.
        - Validates that the integer '1' and the
        """

        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')

    def test_choicefield_3(self):
        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual('J', f.clean('J'))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('John')

    def test_choicefield_4(self):
        """
        Tests the behavior of a ChoiceField with nested choices.
        
        This function validates the ChoiceField's ability to handle nested choices and ensure that only valid choices are accepted. It tests the field's clean method with various inputs, including integers and strings, to verify that the correct choice is returned or an error is raised if an invalid choice is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The ChoiceField is configured with nested choices for 'Numbers' and 'Letters'.
        - The
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
        """
        Tests the behavior of a ChoiceField with a callable choices function.
        
        This function creates a ChoiceField with a callable that returns a list of choices. It then tests the field's clean method to ensure it correctly processes input based on the callable's output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The callable `choices` is defined to return a list of tuples representing choices.
        - A ChoiceField instance `f` is created using this callable.
        - The clean
        """

        def choices():
            return [('J', 'John'), ('P', 'Paul')]
        f = ChoiceField(choices=choices)
        self.assertEqual('J', f.clean('J'))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
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
        
        This function checks the rendering of a ChoiceField with the 'disabled' parameter set to True. The field has two choices: ('J', 'John') and ('P', 'Paul'). The expected output is a <select> widget with the 'disabled' attribute and options for each choice.
        
        Parameters:
        None
        
        Returns:
        None
        
        Asserts:
        The rendered HTML of the widget matches the expected output.
        """

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
