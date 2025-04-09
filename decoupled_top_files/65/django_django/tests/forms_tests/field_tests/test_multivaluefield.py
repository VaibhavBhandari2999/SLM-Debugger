"""
The provided Python file defines several classes and functions related to Django forms and fields. The key components are:

- **ComplexMultiWidget**: A custom widget that combines multiple input fields into a single widget. It includes a `TextInput`, a `SelectMultiple` widget with predefined choices, and a `SplitDateTimeWidget`.
- **ComplexField**: A custom field that uses the `ComplexMultiWidget` to handle complex data inputs. It consists of a `CharField`, a `MultipleChoiceField`, and a `SplitDateTimeField`.
- **ComplexFieldForm**: A Django form that utilizes the `ComplexField` defined above.
- **MultiValueFieldTest**: A test case class that verifies the functionality of the `ComplexField` and `ComplexMulti
"""
from datetime import datetime

from django.core.exceptions import ValidationError
from django.forms import (
    CharField, Form, MultipleChoiceField, MultiValueField, MultiWidget,
    SelectMultiple, SplitDateTimeField, SplitDateTimeWidget, TextInput,
)
from django.test import SimpleTestCase

beatles = (('J', 'John'), ('P', 'Paul'), ('G', 'George'), ('R', 'Ringo'))


class ComplexMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        """
        Initializes a form with specified widgets. The form is initialized with a list of widgets including a TextInput, a SelectMultiple widget with choices from 'beatles', and a SplitDateTimeWidget. The initialization also accepts an optional 'attrs' parameter.
        
        Args:
        attrs (Optional[dict]): Additional attributes for the form.
        
        Returns:
        None: This function does not return any value; it initializes the form object.
        """

        widgets = (
            TextInput(),
            SelectMultiple(choices=beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompresses a compressed string representation of a tuple into its constituent parts.
        
        Args:
        value (str): A comma-separated string representing a tuple containing a string, a list of characters, and a datetime object.
        
        Returns:
        list: A list containing three elements - the first element is a string, the second is a list of characters, and the third is a datetime object.
        """

        if value:
            data = value.split(',')
            return [
                data[0],
                list(data[1]),
                datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S"),
            ]
        return [None, None, None]


class ComplexField(MultiValueField):
    def __init__(self, **kwargs):
        """
        Initializes an instance of a form with specified fields.
        
        Args:
        **kwargs: Additional keyword arguments passed to the superclass initializer.
        
        Fields:
        - CharField: A character field.
        - MultipleChoiceField: A multiple choice field with choices from the `beatles` list.
        - SplitDateTimeField: A split date-time field.
        
        Returns:
        An initialized form object with the specified fields.
        """

        fields = (
            CharField(),
            MultipleChoiceField(choices=beatles),
            SplitDateTimeField(),
        )
        super().__init__(fields, **kwargs)

    def compress(self, data_list):
        """
        Compresses a list of data into a single string.
        
        Args:
        data_list (list): A list containing three elements:
        - The first element is the initial value.
        - The second element is a list of values to be joined together.
        - The third element is the final value.
        
        Returns:
        str or None: A compressed string in the format 'initial_value,joined_values,final_value' if data_list is not empty; otherwise, returns None.
        """

        if data_list:
            return '%s,%s,%s' % (data_list[0], ''.join(data_list[1]), data_list[2])
        return None


class ComplexFieldForm(Form):
    field1 = ComplexField(widget=ComplexMultiWidget())


class MultiValueFieldTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        cls.field = ComplexField(widget=ComplexMultiWidget())
        super().setUpClass()

    def test_clean(self):
        """
        Tests the `clean` method of the field.
        
        Args:
        self (object): The instance of the class containing the field.
        
        Summary:
        This method tests the `clean` method of the field by passing a list of values to it and asserting that the returned value matches the expected output. The `clean` method processes the input list and returns a string with specific formatting.
        
        Args:
        self (object): The instance of the class containing the field.
        
        Returns:
        None
        """

        self.assertEqual(
            self.field.clean(['some text', ['J', 'P'], ['2007-04-25', '6:24:00']]),
            'some text,JP,2007-04-25 06:24:00',
        )

    def test_clean_disabled_multivalue(self):
        """
        Tests the cleaning process of a disabled `ComplexField` with a `ComplexMultiWidget`. The function creates a form with a disabled field and validates different input formats. It ensures that the cleaned data matches the initial data provided.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `ComplexField`: A complex field with a disabled attribute set to True.
        - `ComplexMultiWidget`: A custom widget used for rendering the field.
        - `full_clean()
        """

        class ComplexFieldForm(Form):
            f = ComplexField(disabled=True, widget=ComplexMultiWidget)

        inputs = (
            'some text,JP,2007-04-25 06:24:00',
            ['some text', ['J', 'P'], ['2007-04-25', '6:24:00']],
        )
        for data in inputs:
            with self.subTest(data=data):
                form = ComplexFieldForm({}, initial={'f': data})
                form.full_clean()
                self.assertEqual(form.errors, {})
                self.assertEqual(form.cleaned_data, {'f': inputs[0]})

    def test_bad_choice(self):
        """
        Tests the behavior of the field's clean method when an invalid choice ('X') is provided. Raises a ValidationError with the specified message if the input list contains 'X'. The input list consists of mixed data types including strings, lists, and tuples.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input list contains the invalid choice 'X'.
        
        Important Functions:
        - `self.field.clean`: Cleans and validates the input data.
        - `
        """

        msg = "'Select a valid choice. X is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            self.field.clean(['some text', ['X'], ['2007-04-25', '6:24:00']])

    def test_no_value(self):
        """
        If insufficient data is provided, None is substituted.
        """
        msg = "'This field is required.'"
        with self.assertRaisesMessage(ValidationError, msg):
            self.field.clean(['some text', ['JP']])

    def test_has_changed_no_initial(self):
        self.assertTrue(self.field.has_changed(None, ['some text', ['J', 'P'], ['2007-04-25', '6:24:00']]))

    def test_has_changed_same(self):
        """
        Tests if the field has not changed when given the same input values.
        
        Args:
        self (object): The object instance.
        value1 (str): A string containing text, country code, and date-time.
        value2 (list): A list containing text, country code, and date-time as separate elements.
        
        Returns:
        bool: False if the field has not changed, indicating the inputs are considered the same.
        """

        self.assertFalse(self.field.has_changed(
            'some text,JP,2007-04-25 06:24:00',
            ['some text', ['J', 'P'], ['2007-04-25', '6:24:00']],
        ))

    def test_has_changed_first_widget(self):
        """
        Test when the first widget's data has changed.
        """
        self.assertTrue(self.field.has_changed(
            'some text,JP,2007-04-25 06:24:00',
            ['other text', ['J', 'P'], ['2007-04-25', '6:24:00']],
        ))

    def test_has_changed_last_widget(self):
        """
        Test when the last widget's data has changed. This ensures that it is
        not short circuiting while testing the widgets.
        """
        self.assertTrue(self.field.has_changed(
            'some text,JP,2007-04-25 06:24:00',
            ['some text', ['J', 'P'], ['2009-04-25', '11:44:00']],
        ))

    def test_disabled_has_changed(self):
        f = MultiValueField(fields=(CharField(), CharField()), disabled=True)
        self.assertIs(f.has_changed(['x', 'x'], ['y', 'y']), False)

    def test_form_as_table(self):
        """
        <tr><th><label for="id_field1_0">Field1:</label></th>
        <td><input type="text" name="field1_0" id="id_field1_0" required>
        <select multiple name="field1_1" id="id_field1_1" required>
        <option value="J">John</option>
        <option value="P">Paul</option>
        <option value="G">George</option>
        <option value="R">Ringo</option>
        </select>
        <input type="text" name="field1_2_0" id="id_field1_2_0" required>
        <input type="text" name="field1_2_1" id="id_field1_2_1" required></td></tr>
        """

        form = ComplexFieldForm()
        self.assertHTMLEqual(
            form.as_table(),
            """
            <tr><th><label for="id_field1_0">Field1:</label></th>
            <td><input type="text" name="field1_0" id="id_field1_0" required>
            <select multiple name="field1_1" id="id_field1_1" required>
            <option value="J">John</option>
            <option value="P">Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>
            <input type="text" name="field1_2_0" id="id_field1_2_0" required>
            <input type="text" name="field1_2_1" id="id_field1_2_1" required></td></tr>
            """,
        )

    def test_form_as_table_data(self):
        """
        <tr><th><label for="id_field1_0">Field1:</label></th>
        <td><input type="text" name="field1_0" value="some text" id="id_field1_0" required>
        <select multiple name="field1_1" id="id_field1_1" required>
        <option value="J" selected>John</option>
        <option value="P" selected>Paul</option>
        <option value="G">George</option>
        <option value="R">Ringo</option>
        </select>
        <input type="text" name="field1_2_0" value="2007-04-25" id="id_field1_2_0" required>
        <input type="text" name="field1_2_1" value="06:24:00" id="id_field1_2_1" required></td></tr>
        """

        form = ComplexFieldForm({
            'field1_0': 'some text',
            'field1_1': ['J', 'P'],
            'field1_2_0': '2007-04-25',
            'field1_2_1': '06:24:00',
        })
        self.assertHTMLEqual(
            form.as_table(),
            """
            <tr><th><label for="id_field1_0">Field1:</label></th>
            <td><input type="text" name="field1_0" value="some text" id="id_field1_0" required>
            <select multiple name="field1_1" id="id_field1_1" required>
            <option value="J" selected>John</option>
            <option value="P" selected>Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>
            <input type="text" name="field1_2_0" value="2007-04-25" id="id_field1_2_0" required>
            <input type="text" name="field1_2_1" value="06:24:00" id="id_field1_2_1" required></td></tr>
            """,
        )

    def test_form_cleaned_data(self):
        """
        Tests the `cleaned_data` method of a `ComplexFieldForm` instance.
        
        This function creates an instance of `ComplexFieldForm` with specific data, validates it, and checks if the `cleaned_data` attribute contains the expected value.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `ComplexFieldForm`: The form class being tested.
        - `is_valid()`: Validates the form.
        - `cleaned_data`: The dictionary
        """

        form = ComplexFieldForm({
            'field1_0': 'some text',
            'field1_1': ['J', 'P'],
            'field1_2_0': '2007-04-25',
            'field1_2_1': '06:24:00',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['field1'], 'some text,JP,2007-04-25 06:24:00')
