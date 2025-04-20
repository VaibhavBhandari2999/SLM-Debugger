import datetime

from django import forms
from django.forms import CheckboxSelectMultiple
from django.test import override_settings

from .base import WidgetTest


class CheckboxSelectMultipleTest(WidgetTest):
    widget = CheckboxSelectMultiple

    def test_render_value(self):
        """
        Tests the rendering of a multiple choice checkbox widget with the given choices. The function checks if the rendered HTML matches the expected output.
        
        Parameters:
        - widget: The widget to be rendered, which should be a multiple choice checkbox widget.
        - choices: A list of tuples representing the choices for the widget, where each tuple contains a value and a label.
        - value: The selected value(s) for the widget.
        - html: The expected HTML output as a string.
        
        Returns:
        - None: The function
        """

        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J'], html=(
            """<ul>
            <li><label><input checked type="checkbox" name="beatles" value="J"> John</label></li>
            <li><label><input type="checkbox" name="beatles" value="P"> Paul</label></li>
            <li><label><input type="checkbox" name="beatles" value="G"> George</label></li>
            <li><label><input type="checkbox" name="beatles" value="R"> Ringo</label></li>
            </ul>"""
        ))

    def test_render_value_multiple(self):
        self.check_html(self.widget(choices=self.beatles), 'beatles', ['J', 'P'], html=(
            """<ul>
            <li><label><input checked type="checkbox" name="beatles" value="J"> John</label></li>
            <li><label><input checked type="checkbox" name="beatles" value="P"> Paul</label></li>
            <li><label><input type="checkbox" name="beatles" value="G"> George</label></li>
            <li><label><input type="checkbox" name="beatles" value="R"> Ringo</label></li>
            </ul>"""
        ))

    def test_render_none(self):
        """
        If the value is None, none of the options are selected, even if the
        choices have an empty option.
        """
        self.check_html(self.widget(choices=(('', 'Unknown'),) + self.beatles), 'beatles', None, html=(
            """<ul>
            <li><label><input type="checkbox" name="beatles" value=""> Unknown</label></li>
            <li><label><input type="checkbox" name="beatles" value="J"> John</label></li>
            <li><label><input type="checkbox" name="beatles" value="P"> Paul</label></li>
            <li><label><input type="checkbox" name="beatles" value="G"> George</label></li>
            <li><label><input type="checkbox" name="beatles" value="R"> Ringo</label></li>
            </ul>"""
        ))

    def test_nested_choices(self):
        """
        Tests the rendering of a nested choices field in a widget.
        
        This function checks the rendering of a nested choices field with a widget. The choices are structured as a tuple of tuples, where each inner tuple represents a choice and its sub-choices. The function expects the widget to generate a nested HTML structure with checkboxes for each choice and sub-choice. The function verifies that the generated HTML matches the expected output, including the correct IDs and checked states for the checkboxes.
        
        Parameters:
        - self: The test
        """

        nested_choices = (
            ('unknown', 'Unknown'),
            ('Audio', (('vinyl', 'Vinyl'), ('cd', 'CD'))),
            ('Video', (('vhs', 'VHS'), ('dvd', 'DVD'))),
        )
        html = """
        <ul id="media">
        <li>
        <label for="media_0"><input id="media_0" name="nestchoice" type="checkbox" value="unknown"> Unknown</label>
        </li>
        <li>Audio<ul id="media_1">
        <li>
        <label for="media_1_0">
        <input checked id="media_1_0" name="nestchoice" type="checkbox" value="vinyl"> Vinyl
        </label>
        </li>
        <li>
        <label for="media_1_1"><input id="media_1_1" name="nestchoice" type="checkbox" value="cd"> CD</label>
        </li>
        </ul></li>
        <li>Video<ul id="media_2">
        <li>
        <label for="media_2_0"><input id="media_2_0" name="nestchoice" type="checkbox" value="vhs"> VHS</label>
        </li>
        <li>
        <label for="media_2_1">
        <input checked id="media_2_1" name="nestchoice" type="checkbox" value="dvd"> DVD
        </label>
        </li>
        </ul></li>
        </ul>
        """
        self.check_html(
            self.widget(choices=nested_choices), 'nestchoice', ('vinyl', 'dvd'),
            attrs={'id': 'media'}, html=html,
        )

    def test_nested_choices_without_id(self):
        nested_choices = (
            ('unknown', 'Unknown'),
            ('Audio', (('vinyl', 'Vinyl'), ('cd', 'CD'))),
            ('Video', (('vhs', 'VHS'), ('dvd', 'DVD'))),
        )
        html = """
        <ul>
        <li>
        <label><input name="nestchoice" type="checkbox" value="unknown"> Unknown</label>
        </li>
        <li>Audio<ul>
        <li>
        <label>
        <input checked name="nestchoice" type="checkbox" value="vinyl"> Vinyl
        </label>
        </li>
        <li>
        <label><input name="nestchoice" type="checkbox" value="cd"> CD</label>
        </li>
        </ul></li>
        <li>Video<ul>
        <li>
        <label><input name="nestchoice" type="checkbox" value="vhs"> VHS</label>
        </li>
        <li>
        <label>
        <input checked name="nestchoice" type="checkbox" value="dvd"> DVD
        </label>
        </li>
        </ul></li>
        </ul>
        """
        self.check_html(self.widget(choices=nested_choices), 'nestchoice', ('vinyl', 'dvd'), html=html)

    def test_separate_ids(self):
        """
        Each input gets a separate ID.
        """
        choices = [('a', 'A'), ('b', 'B'), ('c', 'C')]
        html = """
        <ul id="abc">
        <li>
        <label for="abc_0"><input checked type="checkbox" name="letters" value="a" id="abc_0"> A</label>
        </li>
        <li><label for="abc_1"><input type="checkbox" name="letters" value="b" id="abc_1"> B</label></li>
        <li>
        <label for="abc_2"><input checked type="checkbox" name="letters" value="c" id="abc_2"> C</label>
        </li>
        </ul>
        """
        self.check_html(self.widget(choices=choices), 'letters', ['a', 'c'], attrs={'id': 'abc'}, html=html)

    def test_separate_ids_constructor(self):
        """
        Each input gets a separate ID when the ID is passed to the constructor.
        """
        widget = CheckboxSelectMultiple(attrs={'id': 'abc'}, choices=[('a', 'A'), ('b', 'B'), ('c', 'C')])
        html = """
        <ul id="abc">
        <li>
        <label for="abc_0"><input checked type="checkbox" name="letters" value="a" id="abc_0"> A</label>
        </li>
        <li><label for="abc_1"><input type="checkbox" name="letters" value="b" id="abc_1"> B</label></li>
        <li>
        <label for="abc_2"><input checked type="checkbox" name="letters" value="c" id="abc_2"> C</label>
        </li>
        </ul>
        """
        self.check_html(widget, 'letters', ['a', 'c'], html=html)

    @override_settings(USE_L10N=True, USE_THOUSAND_SEPARATOR=True)
    def test_doesnt_localize_input_value(self):
        choices = [
            (1, 'One'),
            (1000, 'One thousand'),
            (1000000, 'One million'),
        ]
        html = """
        <ul>
        <li><label><input type="checkbox" name="numbers" value="1"> One</label></li>
        <li><label><input type="checkbox" name="numbers" value="1000"> One thousand</label></li>
        <li><label><input type="checkbox" name="numbers" value="1000000"> One million</label></li>
        </ul>
        """
        self.check_html(self.widget(choices=choices), 'numbers', None, html=html)

        choices = [
            (datetime.time(0, 0), 'midnight'),
            (datetime.time(12, 0), 'noon'),
        ]
        html = """
        <ul>
        <li><label><input type="checkbox" name="times" value="00:00:00"> midnight</label></li>
        <li><label><input type="checkbox" name="times" value="12:00:00"> noon</label></li>
        </ul>
        """
        self.check_html(self.widget(choices=choices), 'times', None, html=html)

    def test_use_required_attribute(self):
        """
        Tests the `use_required_attribute` method of a widget.
        
        This method checks whether the widget requires a value to be selected. The method is tested with different scenarios:
        - When no choices are provided (None).
        - When an empty list is provided.
        - When a list with some choices is provided.
        
        Parameters:
        - widget: The widget instance to test.
        - choices: A list of choices for the widget.
        
        Returns:
        - A boolean indicating whether the widget requires a value to be selected.
        """

        widget = self.widget(choices=self.beatles)
        # Always False because browser validation would require all checkboxes
        # to be checked instead of at least one.
        self.assertIs(widget.use_required_attribute(None), False)
        self.assertIs(widget.use_required_attribute([]), False)
        self.assertIs(widget.use_required_attribute(['J', 'P']), False)

    def test_value_omitted_from_data(self):
        """
        Tests the behavior of the `value_omitted_from_data` method in the `widget` class.
        
        This method checks whether a value is omitted from the data dictionary. It returns `False` if the value is present in the data dictionary or if the value is not in the choices provided to the widget. The method is tested with an empty data dictionary and a data dictionary containing a field with a value.
        
        Parameters:
        - widget: An instance of the widget class, initialized with a list of choices
        """

        widget = self.widget(choices=self.beatles)
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), False)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_label(self):
        """
        CheckboxSelectMultiple doesn't contain 'for="field_0"' in the <label>
        because clicking that would toggle the first checkbox.
        """
        class TestForm(forms.Form):
            f = forms.MultipleChoiceField(widget=CheckboxSelectMultiple)

        bound_field = TestForm()['f']
        self.assertEqual(bound_field.field.widget.id_for_label('id'), '')
        self.assertEqual(bound_field.label_tag(), '<label>F:</label>')
