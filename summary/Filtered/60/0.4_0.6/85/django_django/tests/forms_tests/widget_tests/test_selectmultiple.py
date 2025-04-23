from django.forms import SelectMultiple

from .base import WidgetTest


class SelectMultipleTest(WidgetTest):
    widget = SelectMultiple
    numeric_choices = (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('0', 'extra'))

    def test_format_value(self):
        """
        Tests the `format_value` method of a widget that handles numeric choices.
        
        Parameters:
        - widget: The widget instance to test, initialized with `choices` set to `self.numeric_choices`.
        
        Returns:
        - None: This function asserts the expected behavior through `assertEqual` checks.
        
        Key Methods:
        - `format_value(value)`: Formats the given value according to the widget's rules.
        
        Key Scenarios:
        1. `format_value(None)`: Should return an empty list `[]`.
        2.
        """

        widget = self.widget(choices=self.numeric_choices)
        self.assertEqual(widget.format_value(None), [])
        self.assertEqual(widget.format_value(''), [''])
        self.assertEqual(widget.format_value([3, 0, 1]), ['3', '0', '1'])

    def test_render_selected(self):
        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J'], html=(
            """<select multiple name="beatles">
            <option value="J" selected>John</option>
            <option value="P">Paul</option>
            <option value="G">George</option>
            <option value="R">Ringo</option>
            </select>"""
        ))

    def test_render_multiple_selected(self):
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
        Tests the behavior of the widget with different sets of selected values and choices. The function checks how the widget renders a multiple select field with pre-selected options.
        
        Parameters:
        - choices (list of tuples): A list of tuples representing the choices for the select field. Each tuple contains two elements: the value and the displayed text.
        - widget (object): The widget object to test.
        - field_name (str): The name of the form field.
        - selected_values (list): A list of selected values
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
        Tests the functionality of a SelectMultiple widget with nested options. The widget is configured with a choice list that includes an outer option and an optgroup containing two inner options. The function verifies that the widget correctly renders the selected options, including the outer option 'outer1' and the inner option 'inner2'. The expected HTML output includes the selected options marked with the 'selected' attribute.
        
        Parameters:
        - widget: The SelectMultiple widget instance configured with the specified choices.
        
        Returns:
        - None: The
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
        widget = self.widget(choices=self.beatles)
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

