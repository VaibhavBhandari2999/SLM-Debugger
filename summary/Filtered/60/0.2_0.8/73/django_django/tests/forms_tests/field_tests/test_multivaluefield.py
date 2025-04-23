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
        widgets = (
            TextInput(),
            SelectMultiple(choices=beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompresses a compressed string into a list of values.
        
        Args:
        value (str): The compressed string to be decompressed. The string is expected to be in the format "string1,string2,string3" where string2 is a comma-separated list.
        
        Returns:
        list: A list containing three elements:
        - The first element is the first string from the input.
        - The second element is a list of strings from the second part of the input.
        - The third
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
        fields = (
            CharField(),
            MultipleChoiceField(choices=beatles),
            SplitDateTimeField(),
        )
        super().__init__(fields, **kwargs)

    def compress(self, data_list):
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
        self.assertEqual(
            self.field.clean(['some text', ['J', 'P'], ['2007-04-25', '6:24:00']]),
            'some text,JP,2007-04-25 06:24:00',
        )

    def test_clean_disabled_multivalue(self):
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
        Tests the behavior of the field's clean method when an invalid choice is provided.
        
        Parameters:
        self: The current test case instance.
        
        Raises:
        ValidationError: If the input does not raise a ValidationError with the expected message.
        
        Input:
        A list containing mixed data types, including a string, a list with a single string, and a list with a date and time.
        
        Output:
        A ValidationError with the message "'Select a valid choice. X is not one of the available choices.'"
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
        Tests the `cleaned_data` method of the `ComplexFieldForm` class.
        
        This function creates an instance of `ComplexFieldForm` with specific data and validates it. It then checks if the `cleaned_data` attribute is as expected.
        
        Parameters:
        - None (The function uses hardcoded data for testing)
        
        Returns:
        - None (The function asserts the correctness of the `cleaned_data` attribute)
        
        Key Data:
        - 'field1_0': 'some text'
        - 'field1
        """

        form = ComplexFieldForm({
            'field1_0': 'some text',
            'field1_1': ['J', 'P'],
            'field1_2_0': '2007-04-25',
            'field1_2_1': '06:24:00',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['field1'], 'some text,JP,2007-04-25 06:24:00')
