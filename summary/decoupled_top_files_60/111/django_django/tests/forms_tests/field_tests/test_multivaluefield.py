from datetime import datetime

from django.core.exceptions import ValidationError
from django.forms import (
    CharField,
    Form,
    MultipleChoiceField,
    MultiValueField,
    MultiWidget,
    SelectMultiple,
    SplitDateTimeField,
    SplitDateTimeWidget,
    TextInput,
)
from django.test import SimpleTestCase

beatles = (("J", "John"), ("P", "Paul"), ("G", "George"), ("R", "Ringo"))


class PartiallyRequiredField(MultiValueField):
    def compress(self, data_list):
        return ",".join(data_list) if data_list else None


class PartiallyRequiredForm(Form):
    f = PartiallyRequiredField(
        fields=(CharField(required=True), CharField(required=False)),
        required=True,
        require_all_fields=False,
        widget=MultiWidget(widgets=[TextInput(), TextInput()]),
    )


class ComplexMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        """
        Initialize a custom form field with specified widgets and attributes.
        
        This method initializes a custom form field with a combination of predefined widgets and optional attributes.
        
        Parameters:
        attrs (dict, optional): Additional attributes to be passed to the form field. Default is None.
        
        Widgets:
        - TextInput: A text input widget.
        - SelectMultiple: A multiple selection widget with choices from the 'beatles' list.
        - SplitDateTimeWidget: A widget for splitting date and time inputs.
        
        Note:
        The
        """

        widgets = (
            TextInput(),
            SelectMultiple(choices=beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            data = value.split(",")
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
        Compresses a list of three elements into a single string.
        
        This function takes a list containing exactly three elements and returns a single string. The first and third elements of the list are concatenated with the second element, which is joined into a single string. If the input list is empty, the function returns None.
        
        Parameters:
        data_list (list): A list containing exactly three elements.
        
        Returns:
        str or None: A compressed string or None if the input list is empty.
        
        Example:
        >>> compress(['
        """

        if data_list:
            return "%s,%s,%s" % (data_list[0], "".join(data_list[1]), data_list[2])
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
            self.field.clean(["some text", ["J", "P"], ["2007-04-25", "6:24:00"]]),
            "some text,JP,2007-04-25 06:24:00",
        )

    def test_clean_disabled_multivalue(self):
        """
        Tests the cleaning functionality of a disabled ComplexField with a ComplexMultiWidget.
        
        This function verifies that the `ComplexField` with `disabled=True` and `ComplexMultiWidget` does not accept any input and always returns the initial value during form cleaning.
        
        Parameters:
        None
        
        Inputs:
        - `data`: A tuple containing two elements. The first element is a string representing the initial value, and the second element is a list representing the expected input data.
        
        Output:
        - None
        
        The function
        """

        class ComplexFieldForm(Form):
            f = ComplexField(disabled=True, widget=ComplexMultiWidget)

        inputs = (
            "some text,JP,2007-04-25 06:24:00",
            ["some text", ["J", "P"], ["2007-04-25", "6:24:00"]],
        )
        for data in inputs:
            with self.subTest(data=data):
                form = ComplexFieldForm({}, initial={"f": data})
                form.full_clean()
                self.assertEqual(form.errors, {})
                self.assertEqual(form.cleaned_data, {"f": inputs[0]})

    def test_bad_choice(self):
        msg = "'Select a valid choice. X is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            self.field.clean(["some text", ["X"], ["2007-04-25", "6:24:00"]])

    def test_no_value(self):
        """
        If insufficient data is provided, None is substituted.
        """
        msg = "'This field is required.'"
        with self.assertRaisesMessage(ValidationError, msg):
            self.field.clean(["some text", ["JP"]])

    def test_has_changed_no_initial(self):
        """
        Tests if the field has changed with the given initial value and a new value. The function checks if the field has changed when provided with `None` as the initial value and a list containing a string and two lists as the new value.
        
        Parameters:
        - self: The current instance of the class.
        
        Returns:
        - bool: True if the field has changed, False otherwise.
        
        Key Parameters:
        - initial: The initial value of the field, in this case, `None`.
        -
        """

        self.assertTrue(
            self.field.has_changed(
                None, ["some text", ["J", "P"], ["2007-04-25", "6:24:00"]]
            )
        )

    def test_has_changed_same(self):
        self.assertFalse(
            self.field.has_changed(
                "some text,JP,2007-04-25 06:24:00",
                ["some text", ["J", "P"], ["2007-04-25", "6:24:00"]],
            )
        )

    def test_has_changed_first_widget(self):
        """
        Test when the first widget's data has changed.
        """
        self.assertTrue(
            self.field.has_changed(
                "some text,JP,2007-04-25 06:24:00",
                ["other text", ["J", "P"], ["2007-04-25", "6:24:00"]],
            )
        )

    def test_has_changed_last_widget(self):
        """
        Test when the last widget's data has changed. This ensures that it is
        not short circuiting while testing the widgets.
        """
        self.assertTrue(
            self.field.has_changed(
                "some text,JP,2007-04-25 06:24:00",
                ["some text", ["J", "P"], ["2009-04-25", "11:44:00"]],
            )
        )

    def test_disabled_has_changed(self):
        f = MultiValueField(fields=(CharField(), CharField()), disabled=True)
        self.assertIs(f.has_changed(["x", "x"], ["y", "y"]), False)

    def test_form_as_table(self):
        form = ComplexFieldForm()
        self.assertHTMLEqual(
            form.as_table(),
            """
            <tr><th><label>Field1:</label></th>
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
        form = ComplexFieldForm(
            {
                "field1_0": "some text",
                "field1_1": ["J", "P"],
                "field1_2_0": "2007-04-25",
                "field1_2_1": "06:24:00",
            }
        )
        self.assertHTMLEqual(
            form.as_table(),
            """
            <tr><th><label>Field1:</label></th>
            <td><input type="text" name="field1_0" value="some text" id="id_field1_0"
                required>
            <select multiple name="field1_1" id="id_field1_1" required>
            <option value="J" selected>John</option>
            <option value="P" selected>Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>
            <input type="text" name="field1_2_0" value="2007-04-25" id="id_field1_2_0"
                required>
            <input type="text" name="field1_2_1" value="06:24:00" id="id_field1_2_1"
                required></td></tr>
            """,
        )

    def test_form_cleaned_data(self):
        """
        Tests the `cleaned_data` method of a `ComplexFieldForm` instance.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - form (ComplexFieldForm): The form instance to be validated.
        
        Keywords:
        - field1_0 (str): The first part of the field1 value.
        - field1_1 (list): A list containing two elements representing the second part of the field1 value.
        - field1_2_0 (str):
        """

        form = ComplexFieldForm(
            {
                "field1_0": "some text",
                "field1_1": ["J", "P"],
                "field1_2_0": "2007-04-25",
                "field1_2_1": "06:24:00",
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data["field1"], "some text,JP,2007-04-25 06:24:00"
        )

    def test_render_required_attributes(self):
        form = PartiallyRequiredForm({"f_0": "Hello", "f_1": ""})
        self.assertTrue(form.is_valid())
        self.assertInHTML(
            '<input type="text" name="f_0" value="Hello" required id="id_f_0">',
            form.as_p(),
        )
        self.assertInHTML('<input type="text" name="f_1" id="id_f_1">', form.as_p())
        form = PartiallyRequiredForm({"f_0": "", "f_1": ""})
        self.assertFalse(form.is_valid())
_f_1">', form.as_p())
        form = PartiallyRequiredForm({"f_0": "", "f_1": ""})
        self.assertFalse(form.is_valid())
