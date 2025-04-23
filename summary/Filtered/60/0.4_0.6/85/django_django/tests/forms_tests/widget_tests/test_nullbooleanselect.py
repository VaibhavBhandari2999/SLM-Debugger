from django.forms import NullBooleanSelect
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        Tests the rendering of a widget for the 'is_cool' field when its value is True.
        
        This function checks the HTML output of the widget for the 'is_cool' field when the value is set to True. The expected HTML output includes a select dropdown with three options: 'Unknown', 'Yes' (selected), and 'No'. The 'Yes' option is selected by default.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function is used for
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
        Tests the rendering of a boolean field with the value 'false'. The function checks if the widget correctly renders the 'is_cool' field as a select dropdown with options for 'Unknown', 'Yes', and 'No'. The selected option is 'No' because the value passed is 'false'. The function uses a predefined check_html method to validate the rendered HTML against an expected output.
        
        Parameters:
        - widget: The widget instance to be rendered.
        - field_name: The name of the field to
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
