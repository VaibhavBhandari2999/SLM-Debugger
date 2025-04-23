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
        __init__(self, attrs=None)
        
        Initialize the form widget.
        
        Parameters:
        - attrs (dict, optional): Additional attributes to be passed to the form widget. Default is None.
        
        Widgets:
        - TextInput: A text input widget for entering text.
        - SelectMultiple: A multiple selection widget with choices from the beatles list.
        - SplitDateTimeWidget: A widget for splitting date and time input.
        
        Note:
        This method initializes the form widget with the specified widgets and additional attributes.
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
        Tests the `clean` method of a disabled `ComplexField` with a `ComplexMultiWidget`.
        
        This function verifies that the `clean` method correctly handles disabled fields
        using a `ComplexMultiWidget`. It ensures that the field's value is not altered
        during the cleaning process, even when initial data is provided.
        
        Parameters:
        - `data`: The initial data to be set for the field. This can be a string or a list
        representing the initial value of the field.
        
        Returns:
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
        """
        Tests the rendering of a form as an HTML table.
        The function takes a `ComplexFieldForm` instance and checks if the rendered HTML matches the expected output. The form is expected to contain a field with multiple input elements including a text input, a select box with multiple options, and two additional text inputs. The function asserts that the rendered HTML matches the provided expected HTML string.
        
        Parameters:
        - form (ComplexFieldForm): The form instance to be rendered and tested.
        
        Returns:
        - None: The
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
