"""
This Python script contains several custom Django form widgets and fields designed to handle complex data inputs. It includes:

- **MyMultiWidget**: A multi-widget that splits a string into two parts using `__` as a delimiter.
- **ComplexMultiWidget**: A more complex multi-widget that processes a comma-separated string into three parts: a string, a list of strings, and a datetime object.
- **ComplexField**: A multi-value field that combines three separate fields into a single string and vice versa.
- **DeepCopyWidget**: A widget used to test the `__deepcopy__()` method of `MultiWidget`.

The script also includes several test methods within the `MultiWidgetTest` class to validate the functionality of these widgets, particularly focusing
"""
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
        Decompresses a given string value.
        
        Args:
        value (str): The input string to be decompressed.
        
        Returns:
        list: A list of two strings obtained by splitting the input value using '__' as the delimiter. If the input is empty, returns ['',''].
        """

        if value:
            return value.split('__')
        return ['', '']


class ComplexMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        """
        __init__(self, attrs=None) - Initializes an instance of the class with specified attributes. Accepts an optional dictionary of attributes. Utilizes the following components: TextInput(), SelectMultiple(choices=WidgetTest.beatles), and SplitDateTimeWidget() to define the widgets for the instance. The super().__init__() method is called to initialize the instance with the defined widgets and attributes.
        """

        widgets = (
            TextInput(),
            SelectMultiple(choices=WidgetTest.beatles),
            SplitDateTimeWidget(),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompresses a compressed string representation of a dataset.
        
        Args:
        value (str): A comma-separated string representing a dataset in the format:
        'column1_value, column2_value_list, timestamp'.
        
        Returns:
        list: A list containing three elements:
        - The first element is `column1_value` (str).
        - The second element is `column2_value_list` (list of str).
        - The third element is `timestamp` (datetime object
        """

        if value:
            data = value.split(',')
            return [
                data[0], list(data[1]), datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
            ]
        return [None, None, None]


class ComplexField(MultiValueField):
    def __init__(self, required=True, widget=None, label=None, initial=None):
        """
        Initializes a form with specified fields, required flag, widget, label, and initial value.
        
        Args:
        required (bool): Indicates if the form field is required.
        widget (Widget): The widget to be used for rendering the form field.
        label (str): The label for the form field.
        initial (Any): The initial value for the form field.
        
        Attributes:
        fields (tuple): A tuple containing the form fields: CharField, MultipleChoiceField, and Split
        """

        fields = (
            CharField(),
            MultipleChoiceField(choices=WidgetTest.beatles),
            SplitDateTimeField(),
        )
        super().__init__(fields, required, widget, label, initial)

    def compress(self, data_list):
        """
        Compresses a list of data into a single string.
        
        Args:
        data_list (list): A list containing three elements:
        - The first element is a string.
        - The second element is a list of strings.
        - The third element is a string.
        
        Returns:
        str: A compressed string in the format "{first_element},{second_element_concatenated},{third_element}" if data_list is not empty; otherwise, returns None.
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
        """
        Initializes a form with a RadioSelect widget and a TextInput widget.
        
        Args:
        choices (list): A list of choices for the RadioSelect widget.
        
        Returns:
        None: This function does not return any value. It initializes the form with the specified widgets.
        
        Attributes:
        widgets (list): A list containing the RadioSelect and TextInput widgets.
        """

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
        """
        Tests the rendering of subwidgets with different names and attributes.
        
        This function creates a `MultiWidget` instance with three subwidgets: an
        empty string widget, a 'big' widget, and a 'small' widget. Each subwidget
        has specific attributes applied. The function then checks the HTML output
        of the widget using the `check_html` method, comparing it against an expected
        HTML string.
        
        Args:
        None
        
        Returns:
        None
        """

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
        Tests the behavior of the `MyMultiWidget` with text inputs.
        
        This function verifies how the `MyMultiWidget` handles different types of input values and attributes. It checks the HTML output for various scenarios involving text inputs, including:
        - Inputting multiple values ('john', 'lennon')
        - Inputting a single concatenated string ('john__lennon')
        - Applying custom attributes (e.g., 'id' attribute)
        
        The function uses the `check_html` method to
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
        """
        Tests the constructor attributes of MyMultiWidget. Creates an instance of MyMultiWidget with specified widgets and additional attributes. Verifies that the generated HTML matches the expected output.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        widget (MyMultiWidget): An instance of MyMultiWidget with specified widgets and attributes.
        html (str): The expected HTML output.
        
        Methods:
        check_html: Compares the generated HTML with the expected output.
        """

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
        Tests the constructor attributes of MyMultiWidget with different configurations.
        
        This function verifies that the `MyMultiWidget` is correctly initialized with various attribute settings, including:
        - A dictionary of attributes (`attrs`) passed directly to the constructor.
        - Multiple widgets with shared attributes.
        - Custom classes applied to the generated HTML inputs.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - `check_html`: Validates the generated HTML against expected output.
        - `
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
        Tests whether the value is omitted from data based on the input fields.
        
        Args:
        widget (MyMultiWidget): The widget instance with multiple input widgets.
        data (dict): The form data.
        files (dict): The form files.
        name (str): The name of the field.
        
        Returns:
        bool: Whether the value is omitted from data.
        """

        widget = MyMultiWidget(widgets=(TextInput(), TextInput()))
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field_0': 'x'}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field_1': 'y'}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field_0': 'x', 'field_1': 'y'}, {}, 'field'), False)

    def test_value_from_datadict_subwidgets_name(self):
        """
        Tests the `value_from_datadict` method of a `MultiWidget` instance with subwidgets named 'x' and an empty string (''). The function iterates through various test cases where different combinations of input data are provided. It uses the `MultiWidget` class with specified widgets for 'x' and an unnamed widget. The `value_from_datadict` method is called with these inputs, and the expected outputs are compared against the actual results. The test cases cover scenarios where no
        """

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
        Tests whether a value is omitted from the data subwidgets name in a MultiWidget.
        
        Args:
        data (dict): The input data to be tested.
        expected (bool): The expected result of the test.
        
        Returns:
        bool: Whether the value is omitted from the data subwidgets name.
        
        Important Functions:
        - `value_omitted_from_data`: Determines if a value is omitted from the data subwidgets name.
        - `MultiWidget`: The widget being tested,
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
        """
        Tests that there is no whitespace between widgets in the generated HTML.
        
        Args:
        widget (MyMultiWidget): The widget to be tested.
        
        Returns:
        None: This function does not return anything, but it checks the HTML output of the widget.
        
        Example:
        >>> widget = MyMultiWidget(widgets=(TextInput, TextInput()))
        >>> test_no_whitespace_between_widgets(widget)
        # This should produce an HTML output without any whitespace between the two input fields.
        """

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
