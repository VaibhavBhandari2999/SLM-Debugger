from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        """
        Tests the behavior of a ChoiceField in a Django form.
        
        This function tests the validation and cleaning behavior of a ChoiceField in Django forms. It checks the following:
        - Raises a ValidationError when the field is left blank or set to None.
        - Correctly converts integer input to the corresponding choice string.
        - Raises a ValidationError with a specific message when an invalid choice is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: When the field is left blank, set to None
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
        """
        Tests the behavior of a ChoiceField with specific choices and validation rules.
        
        This function tests the `clean` method of a `ChoiceField` with the following characteristics:
        - Choices: [('1', 'One'), ('2', 'Two')]
        - Required: False
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Returns:
        - None
        
        Test Cases:
        1. Validates that an empty string is cleaned to an empty string.
        2. Validates that `None` is cleaned to an empty
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
        
        This function tests the `ChoiceField` with a set of choices that includes nested choices and a non-nested choice. It verifies that the field correctly validates and cleans input values based on the provided choices.
        
        Parameters:
        - None (The function uses internal parameters defined within the test case)
        
        Returns:
        - None (The function asserts expected outcomes through internal test case mechanisms)
        
        Key Points:
        - The `ChoiceField` is configured with the following choices:
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
        
        This function checks if a ChoiceField with the 'disabled' attribute set to True is rendered correctly in HTML. The field has two choices: 'J' with the label 'John' and 'P' with the label 'Paul'. The expected output is a <select> element with the 'disabled' attribute and two <option> elements for each choice.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The 'choices'
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_choicefield_enumeration(self):
        """
        Tests the behavior of a ChoiceField with an enumeration.
        
        This function creates a ChoiceField using the `FirstNames` enumeration and tests its clean method. The `FirstNames` enumeration is defined with two choices: 'J' for 'John' and 'P' for 'Paul'. The function verifies that the clean method correctly returns the expected value when a valid choice ('J') is passed and raises a ValidationError with a specific error message when an invalid choice ('3') is passed.
        
        Parameters:
        """

        class FirstNames(models.TextChoices):
            JOHN = 'J', 'John'
            PAUL = 'P', 'Paul'

        f = ChoiceField(choices=FirstNames.choices)
        self.assertEqual(f.clean('J'), 'J')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
