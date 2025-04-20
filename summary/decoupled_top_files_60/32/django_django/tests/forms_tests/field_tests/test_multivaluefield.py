from datetime import datetime

from django.forms import (
    CharField, Form, MultipleChoiceField, MultiValueField, MultiWidget,
    SelectMultiple, SplitDateTimeField, SplitDateTimeWidget, TextInput,
    ValidationError,
)
from django.test import SimpleTestCase

beatles = (('J', 'John'), ('P', 'Paul'), ('G', 'George'), ('R', 'Ringo'))


class ComplexMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        """
        Initialize a custom form field or widget.
        
        This method initializes a custom form field or widget with specified attributes.
        
        Parameters:
        attrs (dict, optional): Additional attributes to be passed to the form field or widget.
        
        Attributes:
        widgets (tuple): A tuple containing the widgets to be used in the form field or widget. The tuple includes:
        - TextInput: A text input widget.
        - SelectMultiple: A multiple selection widget with choices from the 'beatles' list.
        - SplitDateTime
        """

        widgets = (
            TextInput(),
            SelectMultiple(choices=beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
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
        """
        Compresses a list of data into a single string.
        
        This function takes a list of three elements: the first and third elements are strings, and the second element is a list of strings. It concatenates the first and third elements with the second element, which is joined into a single string. The resulting string is returned.
        
        Parameters:
        data_list (list): A list containing three elements. The first and third elements are strings, and the second element is a list of strings.
        
        Returns:
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
        self.assertEqual(
            self.field.clean(['some text', ['J', 'P'], ['2007-04-25', '6:24:00']]),
            'some text,JP,2007-04-25 06:24:00',
        )

    def test_clean_disabled_multivalue(self):
        """
        Tests the cleaning process for a disabled multivalue field in a form.
        
        This function checks the cleaning behavior of a disabled `ComplexField` with a `ComplexMultiWidget`. It ensures that the field's value is cleaned correctly, even when the field is disabled.
        
        Parameters:
        - `data` (tuple): A tuple containing two elements. The first element is the initial data for the form, and the second element is the expected cleaned data.
        
        Returns:
        - None: The function asserts the correctness of
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
        """
        Tests the rendering of a form with a complex field using the `as_table` method.
        
        This function creates an instance of `ComplexFieldForm` with specific data and then checks if the HTML output matches the expected table format. The form includes a text input, a multiple select dropdown, and two date/time inputs. The `assertHTMLEqual` method is used to validate the HTML output.
        
        Parameters:
        - None (The function uses internal form data and does not accept external parameters).
        
        Returns:
        -
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
        form = ComplexFieldForm({
            'field1_0': 'some text',
            'field1_1': ['J', 'P'],
            'field1_2_0': '2007-04-25',
            'field1_2_1': '06:24:00',
        })
        form.is_valid()
        self.assertEqual(form.cleaned_data['field1'], 'some text,JP,2007-04-25 06:24:00')

