"""
This Python file contains unit tests for the `SelectMultiple` widget in Django. The `SelectMultipleTest` class inherits from `WidgetTest` and defines several test methods to validate the behavior of the `SelectMultiple` widget under different scenarios:

1. **`test_format_value`**: Tests how the widget formats input values into a list of strings based on its choices.
2. **`test_render_selected`**: Verifies that the correct options are selected when rendering the widget with a single selected value.
3. **`test_render_multiple_selected`**: Ensures that multiple options are correctly marked as selected when rendering the widget with multiple selected values.
4. **`test_render_none`**: Checks that no options are selected when the input value
"""
from django.forms import SelectMultiple

from .base import WidgetTest


class SelectMultipleTest(WidgetTest):
    widget = SelectMultiple
    numeric_choices = (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('0', 'extra'))

    def test_format_value(self):
        """
        Tests the `format_value` method of the widget.
        
        This method is responsible for formatting the input value according to the widget's choices. It handles three cases:
        - When the input value is `None`, it returns an empty list.
        - When the input value is an empty string, it returns a list containing an empty string.
        - When the input value is a list of numeric choices, it formats each element as a string and returns the list of formatted strings.
        
        Args:
        """

        widget = self.widget(choices=self.numeric_choices)
        self.assertEqual(widget.format_value(None), [])
        self.assertEqual(widget.format_value(''), [''])
        self.assertEqual(widget.format_value([3, 0, 1]), ['3', '0', '1'])

    def test_render_selected(self):
        """
        <select multiple name="beatles">
        <option value="J" selected>John</option>
        <option value="P">Paul</option>
        <option value="G">George</option>
        <option value="R">Ringo</option>
        </select>
        """

        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J'], html=(
            """<select multiple name="beatles">
            <option value="J" selected>John</option>
            <option value="P">Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_render_multiple_selected(self):
        """
        <select multiple name="beatles">
        <option value="J" selected>John</option>
        <option value="P" selected>Paul</option>
        <option value="G">George</option>
        <option value="R">Ringo</option>
        </select>
        """

        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J', 'P'], html=(
            """<select multiple name="beatles">
            <option value="J" selected>John</option>
            <option value="P" selected>Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_render_none(self):
        """
        If the value is None, none of the options are selected, even if the
        choices have an empty option.
        """
        self.check_html(self.widget(choices=(('', 'Unknown'),) + self.beatles), 'beatles', None, html=(
            """<select multiple name="beatles">
            <option value="">Unknown</option>
            <option value="J">John</option>
            <option value="P">Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_render_value_label(self):
        """
        If the value corresponds to a label (but not to an option value), none
        of the options are selected.
        """
        self.check_html(self.widget(choices=self.beatles), 'beatles', ['John'], html=(
            """<select multiple name="beatles">
            <option value="J">John</option>
            <option value="P">Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_multiple_options_same_value(self):
        """
        Multiple options with the same value can be selected (#8103).
        """
        self.check_html(self.widget(choices=self.numeric_choices), 'choices', ['0'], html=(
            """<select multiple name="choices">
            <option value="0" selected>0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="0" selected>extra</option>
            </select>"""
        ))

    def test_multiple_values_invalid(self):
        """
        If multiple values are given, but some of them are not valid, the valid
        ones are selected.
        """
        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J', 'G', 'foo'], html=(
            """<select multiple name="beatles">
            <option value="J" selected>John</option>
            <option value="P">Paul</option>
            <option value="G" selected>George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_compare_string(self):
        """
        <select multiple name="nums">
        <option value="1">1</option>
        <option value="2" selected>2</option>
        <option value="3">3</option>
        </select>
        """

        choices = [('1', '1'), ('2', '2'), ('3', '3')]

        self.check_html(self.widget(choices=choices), 'nums', [2], html=(
            """<select multiple name="nums">
            <option value="1">1</option>
            <option value="2" selected>2</option>
            <option value="3">3</option>
            </select>"""
        ))

        self.check_html(self.widget(choices=choices), 'nums', ['2'], html=(
            """<select multiple name="nums">
            <option value="1">1</option>
            <option value="2" selected>2</option>
            <option value="3">3</option>
            </select>"""
        ))

        self.check_html(self.widget(choices=choices), 'nums', [2], html=(
            """<select multiple name="nums">
            <option value="1">1</option>
            <option value="2" selected>2</option>
            <option value="3">3</option>
            </select>"""
        ))

    def test_optgroup_select_multiple(self):
        """
        <select multiple name="nestchoice">
        <option value="outer1" selected>Outer 1</option>
        <optgroup label="Group &quot;1&quot;">
        <option value="inner1">Inner 1</option>
        <option value="inner2" selected>Inner 2</option>
        </optgroup>
        </select>
        """

        widget = SelectMultiple(choices=(
            ('outer1', 'Outer 1'),
            ('Group "1"', (('inner1', 'Inner 1'), ('inner2', 'Inner 2'))),
        ))
        self.check_html(widget, 'nestchoice', ['outer1', 'inner2'], html=(
            """<select multiple name="nestchoice">
            <option value="outer1" selected>Outer 1</option>
            <optgroup label="Group &quot;1&quot;">
            <option value="inner1">Inner 1</option>
            <option value="inner2" selected>Inner 2</option>
            </optgroup>
            </select>"""
        ))

    def test_value_omitted_from_data(self):
        """
        Tests whether the value is omitted from data.
        
        Args:
        widget (Widget): The widget instance with choices set to beatles.
        data (dict): The form data.
        files (dict): The form files.
        name (str): The field name.
        
        Returns:
        bool: True if the value is not omitted, otherwise False.
        """

        widget = self.widget(choices=self.beatles)
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)
