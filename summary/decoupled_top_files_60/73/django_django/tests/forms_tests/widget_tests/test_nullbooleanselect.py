from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        Tests the rendering of a widget for the 'is_cool' field when its value is True.
        This function checks if the widget correctly renders a select dropdown with the options 'Unknown', 'Yes', and 'No'.
        When the value is True, the 'Yes' option is selected.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None: This function is used for asserting the correctness of the widget rendering and does not return any value.
        """

        self.check_html(self.widget, 'is_cool', True, html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_false(self):
        self.check_html(self.widget, 'is_cool', False, html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true">Yes</option>
            <option value="false" selected>No</option>
            </select>"""
        ))

    def test_render_none(self):
        self.check_html(self.widget, 'is_cool', None, html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_unknown(self):
        """
        Tests the rendering of an unknown value in a select widget.
        
        This function checks the HTML output of a widget when rendering a field named 'is_cool' with an unknown value. The widget is expected to generate a select element with three options: 'Unknown', 'Yes', and 'No'. The 'Unknown' option should be selected by default.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function is used for asserting the expected HTML output and does not return any
        """

        self.check_html(self.widget, 'is_cool', 'unknown', html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_true(self):
        self.check_html(self.widget, 'is_cool', 'true', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_false(self):
        """
        Tests the rendering of a boolean field with the value 'false'. The function checks if the widget renders the select field correctly with the given value. The expected HTML output is provided as a keyword argument to the check_html method.
        
        Parameters:
        - self: The test case instance.
        
        Keywords:
        - widget: The widget instance to be tested.
        - field_name: The name of the field ('is_cool' in this case).
        - value: The value to be set for the field ('false' in
        """

        self.check_html(self.widget, 'is_cool', 'false', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true">Yes</option>
            <option value="false" selected>No</option>
            </select>"""
        ))

    def test_render_value_1(self):
        self.check_html(self.widget, 'is_cool', '1', html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_2(self):
        """
        Tests the rendering of a boolean field value '2' in a dropdown select widget. The function checks if the rendered HTML matches the expected output. The dropdown options include 'Unknown', 'Yes', and 'No'. The value '2' is selected in the dropdown.
        
        Parameters:
        - self: The instance of the test class.
        
        Returns:
        - None: This function is used for testing and does not return any value. It asserts that the rendered HTML matches the expected output.
        """

        self.check_html(self.widget, 'is_cool', '2', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_3(self):
        self.check_html(self.widget, 'is_cool', '3', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true">Yes</option>
            <option value="false" selected>No</option>
            </select>"""
        ))

    @override_settings(USE_L10N=True)
    def test_l10n(self):
        """
        The NullBooleanSelect widget's options are lazily localized (#17190).
        """
        widget = NullBooleanSelect()

        with translation.override('de-at'):
            self.check_html(widget, 'id_bool', True, html=(
                """
                <select name="id_bool">
                    <option value="unknown">Unbekannt</option>
                    <option value="true" selected>Ja</option>
                    <option value="false">Nein</option>
                </select>
                """
            ))
