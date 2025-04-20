from django.forms import SelectMultiple

from .base import WidgetTest


class SelectMultipleTest(WidgetTest):
    widget = SelectMultiple
    numeric_choices = (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('0', 'extra'))

    def test_format_value(self):
        """
        Tests the `format_value` method of a widget with numeric choices.
        
        This method checks how the widget handles different input values for formatting. It expects the widget to return an empty list when given None, a single-element list containing an empty string when given an empty string, and a list of formatted strings when given a list of integers.
        
        Parameters:
        - self: The test case instance.
        
        Key Parameters:
        - choices (list): The choices for the widget, which are set to numeric choices in this test
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
        Tests the functionality of the widget with multiple choice options. The widget is initialized with a list of choices and tested for different selected values.
        
        Parameters:
        choices (list of tuples): A list of tuples representing the choices for the widget, where each tuple contains a value and a display string.
        
        Returns:
        None: This function is used for testing and does not return any value. It asserts the correctness of the widget's HTML output based on the provided choices and selected values.
        
        Test Cases:
        1.
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
        Tests the behavior of the `value_omitted_from_data` method in the `widget` class.
        
        This method checks if a value is omitted from the data dictionary. The method takes three parameters:
        - `data`: A dictionary containing the form data.
        - `files`: A dictionary containing the form files.
        - `name`: The name of the form field.
        
        The method returns `False` if the value is not omitted, meaning it is either present in the data or has a default value.
        """

        widget = self.widget(choices=self.beatles)
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)
