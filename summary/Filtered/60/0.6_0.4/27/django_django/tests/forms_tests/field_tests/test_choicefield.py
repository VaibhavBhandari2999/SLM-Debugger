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
        Tests the behavior of a ChoiceField with the following parameters:
        - choices: A list of tuples where each tuple contains a value and a display string for the choices.
        - required: A boolean indicating whether the field is required.
        
        Key Methods:
        - clean: Validates and cleans the input value.
        
        Key Parameters:
        - choices: List of tuples, each containing a value and a display string.
        - required: Boolean, if True, the field must have a value.
        
        Key Outputs:
        - Returns the cleaned value
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
        
        This function checks if a ChoiceField with the 'disabled' attribute set to True is rendered correctly in HTML. The field has two choices: ('J', 'John') and ('P', 'Paul'). The expected output is a <select> element with the 'disabled' attribute and two <option> elements corresponding to the choices.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The rendered HTML of the field is compared to the expected
        """

        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )
