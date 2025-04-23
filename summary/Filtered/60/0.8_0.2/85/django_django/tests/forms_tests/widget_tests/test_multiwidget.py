import copy
from datetime import datetime

from django.forms import (
    CharField, FileInput, MultipleChoiceField, MultiValueField, MultiWidget,
    RadioSelect, SelectMultiple, SplitDateTimeField, SplitDateTimeWidget,
    TextInput,
)

from .base import WidgetTest


class MyMultiWidget(MultiWidget):
    def decompress(self, value):
        """
        Decompresses a compressed string value.
        
        Args:
        value (str): The compressed string to be decompressed. If the value is empty, it defaults to an empty list.
        
        Returns:
        list: A list of strings resulting from the decompression of the input value. If the input is empty, returns a list with two empty strings.
        """

        if value:
            return value.split('__')
        return ['', '']


class ComplexMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        """
        Initialize a new instance of the class.
        
        This method initializes a new instance of the class with the specified attributes.
        
        Parameters:
        attrs (dict, optional): Additional attributes to be set on the instance. Defaults to None.
        
        Attributes:
        widgets (tuple): A tuple containing the widgets to be used in the instance. The tuple includes TextInput, SelectMultiple, and SplitDateTimeWidget.
        
        Returns:
        None: This method does not return any value. It is used to set up the instance's initial state
        """

        widgets = (
            TextInput(),
            SelectMultiple(choices=WidgetTest.beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            data = value.split(',')
            return [
                data[0], list(data[1]), datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
            ]
        return [None, None, None]


class ComplexField(MultiValueField):
    def __init__(self, required=True, widget=None, label=None, initial=None):
        fields = (
            CharField(),
            MultipleChoiceField(choices=WidgetTest.beatles),
            SplitDateTimeField(),
        )
        super().__init__(fields, required, widget, label, initial)

    def compress(self, data_list):
        """
        Compresses a list of data into a single string.
        
        This function takes a list of three elements and returns a compressed string. The first and third elements of the list are included as is, while the second element is joined into a single string. If the input list is empty, the function returns None.
        
        Parameters:
        data_list (list): A list containing exactly three elements.
        
        Returns:
        str or None: A compressed string if the input list is not empty, otherwise None.
        """

        if data_list:
            return '%s,%s,%s' % (
                data_list[0], ''.join(data_list[1]), data_list[2],
            )
        return None


class DeepCopyWidget(MultiWidget):
    """
    Used to test MultiWidget.__deepcopy__().
    """
    def __init__(self, choices=[]):
        widgets = [
            RadioSelect(choices=choices),
            TextInput,
        ]
        super().__init__(widgets)

    def _set_choices(self, choices):
        """
        When choices are set for this widget, we want to pass those along to
        the Select widget.
        """
        self.widgets[0].choices = choices

    def _get_choices(self):
        """
        The choices for this widget are the Select widget's choices.
        """
        return self.widgets[0].choices
    choices = property(_get_choices, _set_choices)


class MultiWidgetTest(WidgetTest):
    def test_subwidgets_name(self):
        widget = MultiWidget(
            widgets={
                '': TextInput(),
                'big': TextInput(attrs={'class': 'big'}),
                'small': TextInput(attrs={'class': 'small'}),
            },
        )
        self.check_html(widget, 'name', ['John', 'George', 'Paul'], html=(
            '<input type="text" name="name" value="John">'
            '<input type="text" name="name_big" value="George" class="big">'
            '<input type="text" name="name_small" value="Paul" class="small">'
        ))

    def test_text_inputs(self):
        """
        Tests the behavior of a custom widget, MyMultiWidget, which is a collection of TextInput widgets. The function checks the HTML output for different input scenarios.
        
        Parameters:
        - widget: An instance of MyMultiWidget, which is a collection of TextInput widgets with different classes.
        - field: The name of the form field being tested.
        - value: The input value for the form field, which can be a list or a single string.
        - attrs: Additional attributes to be applied to the input fields,
        """

        widget = MyMultiWidget(
            widgets=(
                TextInput(attrs={'class': 'big'}),
                TextInput(attrs={'class': 'small'}),
            )
        )
        self.check_html(widget, 'name', ['john', 'lennon'], html=(
            '<input type="text" class="big" value="john" name="name_0">'
            '<input type="text" class="small" value="lennon" name="name_1">'
        ))
        self.check_html(widget, 'name', 'john__lennon', html=(
            '<input type="text" class="big" value="john" name="name_0">'
            '<input type="text" class="small" value="lennon" name="name_1">'
        ))
        self.check_html(widget, 'name', 'john__lennon', attrs={'id': 'foo'}, html=(
            '<input id="foo_0" type="text" class="big" value="john" name="name_0">'
            '<input id="foo_1" type="text" class="small" value="lennon" name="name_1">'
        ))

    def test_constructor_attrs(self):
        widget = MyMultiWidget(
            widgets=(
                TextInput(attrs={'class': 'big'}),
                TextInput(attrs={'class': 'small'}),
            ),
            attrs={'id': 'bar'},
        )
        self.check_html(widget, 'name', ['john', 'lennon'], html=(
            '<input id="bar_0" type="text" class="big" value="john" name="name_0">'
            '<input id="bar_1" type="text" class="small" value="lennon" name="name_1">'
        ))

    def test_constructor_attrs_with_type(self):
        """
        Test the constructor attributes with type.
        
        This function checks the behavior of the `MyMultiWidget` constructor when provided with specific attributes. It tests the widget with different configurations and verifies the generated HTML output.
        
        Parameters:
        - attrs (dict): A dictionary containing the attributes to be passed to the widget, including the 'type' attribute.
        
        Returns:
        None: This function is used for testing and does not return any value. It asserts the correctness of the widget's HTML output.
        
        Test Cases:
        1
        """

        attrs = {'type': 'number'}
        widget = MyMultiWidget(widgets=(TextInput, TextInput()), attrs=attrs)
        self.check_html(widget, 'code', ['1', '2'], html=(
            '<input type="number" value="1" name="code_0">'
            '<input type="number" value="2" name="code_1">'
        ))
        widget = MyMultiWidget(widgets=(TextInput(attrs), TextInput(attrs)), attrs={'class': 'bar'})
        self.check_html(widget, 'code', ['1', '2'], html=(
            '<input type="number" value="1" name="code_0" class="bar">'
            '<input type="number" value="2" name="code_1" class="bar">'
        ))

    def test_value_omitted_from_data(self):
        """
        Tests the behavior of the `value_omitted_from_data` method for a custom widget.
        
        This method checks whether the value is omitted from the data dictionary when the widget is rendered.
        
        Parameters:
        - widget (MyMultiWidget): The custom widget instance to test.
        - data (dict): The data dictionary containing the widget's values.
        - files (dict): The files dictionary containing the widget's files.
        - name (str): The name of the field being tested.
        
        Returns:
        """

        widget = MyMultiWidget(widgets=(TextInput(), TextInput()))
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field_0': 'x'}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field_1': 'y'}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field_0': 'x', 'field_1': 'y'}, {}, 'field'), False)

    def test_value_from_datadict_subwidgets_name(self):
        widget = MultiWidget(widgets={'x': TextInput(), '': TextInput()})
        tests = [
            ({}, [None, None]),
            ({'field': 'x'}, [None, 'x']),
            ({'field_x': 'y'}, ['y', None]),
            ({'field': 'x', 'field_x': 'y'}, ['y', 'x']),
        ]
        for data, expected in tests:
            with self.subTest(data):
                self.assertEqual(
                    widget.value_from_datadict(data, {}, 'field'),
                    expected,
                )

    def test_value_omitted_from_data_subwidgets_name(self):
        """
        Tests the `value_omitted_from_data` method of a `MultiWidget` instance.
        
        This method checks whether a value is omitted from the data when the corresponding subwidget name is empty.
        
        Parameters:
        - data (dict): The data dictionary to test.
        - expected (bool): The expected result of the `value_omitted_from_data` method.
        
        The `MultiWidget` instance has the following configuration:
        - `widgets`: A dictionary with keys 'x' and '', each mapped to a
        """

        widget = MultiWidget(widgets={'x': TextInput(), '': TextInput()})
        tests = [
            ({}, True),
            ({'field': 'x'}, False),
            ({'field_x': 'y'}, False),
            ({'field': 'x', 'field_x': 'y'}, False),
        ]
        for data, expected in tests:
            with self.subTest(data):
                self.assertIs(
                    widget.value_omitted_from_data(data, {}, 'field'),
                    expected,
                )

    def test_needs_multipart_true(self):
        """
        needs_multipart_form should be True if any widgets need it.
        """
        widget = MyMultiWidget(widgets=(TextInput(), FileInput()))
        self.assertTrue(widget.needs_multipart_form)

    def test_needs_multipart_false(self):
        """
        needs_multipart_form should be False if no widgets need it.
        """
        widget = MyMultiWidget(widgets=(TextInput(), TextInput()))
        self.assertFalse(widget.needs_multipart_form)

    def test_nested_multiwidget(self):
        """
        MultiWidgets can be composed of other MultiWidgets.
        """
        widget = ComplexMultiWidget()
        self.check_html(widget, 'name', 'some text,JP,2007-04-25 06:24:00', html=(
            """
            <input type="text" name="name_0" value="some text">
            <select multiple name="name_1">
                <option value="J" selected>John</option>
                <option value="P" selected>Paul</option>
                <option value="G">George</option>
                <option value="R">Ringo</option>
            </select>
            <input type="text" name="name_2_0" value="2007-04-25">
            <input type="text" name="name_2_1" value="06:24:00">
            """
        ))

    def test_no_whitespace_between_widgets(self):
        widget = MyMultiWidget(widgets=(TextInput, TextInput()))
        self.check_html(widget, 'code', None, html=(
            '<input type="text" name="code_0">'
            '<input type="text" name="code_1">'
        ), strict=True)

    def test_deepcopy(self):
        """
        MultiWidget should define __deepcopy__() (#12048).
        """
        w1 = DeepCopyWidget(choices=[1, 2, 3])
        w2 = copy.deepcopy(w1)
        w2.choices = [4, 5, 6]
        # w2 ought to be independent of w1, since MultiWidget ought
        # to make a copy of its sub-widgets when it is copied.
        self.assertEqual(w1.choices, [1, 2, 3])
es, [1, 2, 3])
