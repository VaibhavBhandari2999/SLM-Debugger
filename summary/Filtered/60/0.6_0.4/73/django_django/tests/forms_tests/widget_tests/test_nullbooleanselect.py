from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        Tests the rendering of the 'is_cool' widget with the value 'True'.
        
        This function checks the HTML output of the widget when the 'is_cool' attribute is set to 'True'.
        The expected HTML includes a select dropdown with options for 'Unknown', 'Yes', and 'No', where 'Yes' is selected.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None: This function is used for asserting the expected output and does not return any value.
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
        """
        Tests the rendering of a widget for the 'is_cool' field when its value is None. The widget is expected to display a select dropdown with three options: 'Unknown', 'Yes', and 'No'. The 'Unknown' option is selected by default.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function is a test case and does not return any value. It asserts the expected HTML output against the actual output of the widget.
        """

        self.check_html(self.widget, 'is_cool', None, html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_unknown(self):
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
        self.check_html(self.widget, 'is_cool', '2', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_3(self):
        """
        Tests the rendering of a select widget for the 'is_cool' field with the value '3'.
        The function checks that the rendered HTML matches the expected output.
        The expected HTML includes a select element with the name 'is_cool',
        containing three options: 'Unknown', 'Yes', and 'No'.
        The 'No' option is selected by default.
        
        Parameters:
        - widget: The widget instance to be rendered.
        - field_name: The name of the field ('is
        """

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
