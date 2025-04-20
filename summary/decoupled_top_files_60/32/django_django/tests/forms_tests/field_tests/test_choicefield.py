from django.forms import ChoiceField, Form, ValidationError
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
        Test the behavior of a ChoiceField with specific choices and validation rules.
        
        This function tests the `clean` method of a ChoiceField with the following characteristics:
        - Choices: [('1', 'One'), ('2', 'Two')]
        - Required: False
        
        Key Parameters:
        - No explicit parameters are passed in the function, but it implicitly uses the `ChoiceField` class with the specified choices and required status.
        
        Key Keywords:
        - choices: List of tuples representing the choices for the field.
        - required
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
        Tests that a callable passed to the choices parameter of a ChoiceField may evaluate to different values depending on when it is called.
        
        This function creates a form with a ChoiceField that uses a callable for its choices. The callable returns a list of choices, which is updated between tests. The function asserts that the choices displayed in the form are updated accordingly.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Behavior:
        - Defines a form with a ChoiceField using a callable for choices.
        -
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
        
        This function checks if a ChoiceField with specified choices and a disabled state renders correctly. The key parameters are:
        - `choices`: A list of tuples where each tuple contains a value and a label for the options in the dropdown.
        - `disabled`: A boolean indicating whether the field should be disabled.
        
        The function asserts that the rendered widget matches the expected HTML output, which includes the disabled attribute on the select element and the correct option values and labels.
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )
