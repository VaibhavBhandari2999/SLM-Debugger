"""
The provided Python file contains unit tests for the `ChoiceField` class in Django forms. These tests cover various scenarios such as handling empty values, validating choices, and testing the behavior of `ChoiceField` with different types of choices (including nested choices and callable choices). The tests are implemented within the `ChoiceFieldTest` class, which inherits from `FormFieldAssertionsMixin` and `SimpleTestCase`. Each test method focuses on a specific aspect of the `ChoiceField` behavior, ensuring comprehensive coverage of its functionality. The tests also demonstrate how the `ChoiceField` interacts with other components like `Form` and `ValidationError`. The file serves as a valuable resource for verifying the correctness and robustness of the `ChoiceField` implementation in Django forms.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ChoiceField, Form
from django.test import SimpleTestCase

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        """
        Tests the behavior of a ChoiceField in Django forms.
        
        This function tests various scenarios involving a ChoiceField with predefined choices. It checks how the field handles empty values, None, integer inputs, string inputs, and invalid choices.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: When an invalid value is passed to the clean method.
        
        Important Functions:
        - `ChoiceField`: The form field being tested.
        - `clean`: Method used to validate
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
        
        This function tests the `clean` method of a `ChoiceField` instance that has been initialized with
        predefined choices and a `required=False` parameter. It verifies how the field handles various inputs,
        including empty strings, `None`, numeric values, and invalid choices.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `ChoiceField`: The field type being tested.
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
        """
        Tests the clean method of a ChoiceField with specific choices. The function creates a ChoiceField with choices ('J', 'John') and ('P', 'Paul'). It verifies that the field correctly returns 'J' when cleaned with 'J', and raises a ValidationError with the specified message when cleaned with 'John'. This tests the validation and cleaning functionality of the ChoiceField.
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual('J', f.clean('J'))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('John')

    def test_choicefield_4(self):
        """
        Tests the behavior of a ChoiceField with nested choices. The field accepts integers or strings corresponding to the choices ('Numbers' with subchoices '1' and '2', 'Letters' with subchoices '3' and '4', and '5' as a standalone choice). It validates inputs and raises a ValidationError if an invalid choice is provided.
        
        Args:
        None (This function is part of a test suite and does not take any arguments).
        
        Returns:
        None (This function performs
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
        Tests the behavior of a ChoiceField with callable choices.
        
        This function creates a ChoiceField using a callable function `choices` that returns a list of tuples representing the field's choices. The `clean` method is then called on the field instance with the value 'J' to validate and clean the input.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - ChoiceField: Creates a choice field with callable choices.
        - choices: Callable function that returns a
        """

        def choices():
            return [('J', 'John'), ('P', 'Paul')]
        f = ChoiceField(choices=choices)
        self.assertEqual('J', f.clean('J'))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
        """
        Tests that a callable used for choices in a ChoiceField may evaluate to different values depending on when it is called.
        
        This function evaluates a form with a ChoiceField using a callable for its choices. The callable returns a list of choices, which changes between tests, demonstrating that the callable can produce different results each time it is evaluated.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `ChoiceField`: Creates a form field with choices defined by a callable.
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
        Tests the rendering of a disabled ChoiceField widget.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - ChoiceField: Creates a choice field with specified choices and disabled status.
        - assertWidgetRendersTo: Asserts that the rendered widget matches the expected HTML output.
        
        Input Variables:
        - choices: A list of tuples containing the choices for the field (e.g., [('J', 'John'), ('P', 'Paul')]).
        
        Output
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_choicefield_enumeration(self):
        """
        Tests the validation of a ChoiceField using TextChoices enumeration.
        
        This function creates a ChoiceField with choices defined by the `FirstNames` TextChoices enumeration. It then tests the field's clean method by passing a valid choice ('J') and an invalid choice ('3'), expecting the clean method to return the valid choice and raise a ValidationError for the invalid choice.
        
        Args:
        None (This function is part of a test suite and does not take any arguments).
        
        Returns:
        None (
        """

        class FirstNames(models.TextChoices):
            JOHN = 'J', 'John'
            PAUL = 'P', 'Paul'

        f = ChoiceField(choices=FirstNames.choices)
        self.assertEqual(f.clean('J'), 'J')
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')
