from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        Tests the rendering of a widget for the 'is_cool' field with a boolean value of True.
        
        This function checks the HTML output of the widget when the 'is_cool' field is set to True. The expected HTML includes a select dropdown with options for 'Unknown', 'Yes', and 'No'. The 'Yes' option should be selected.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function is used for asserting the correct HTML output and does not
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
        
        This function checks the HTML output of the widget when the value 'unknown' is passed for the attribute 'is_cool'. The expected HTML output includes a select element with options for 'unknown', 'true', and 'false'. The 'unknown' option is selected by default.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None: This function is used for asserting the expected HTML output and does not return
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
        Tests the rendering of a widget for the 'is_cool' field with a value of '3'. The widget is expected to generate a select dropdown with three options: 'Unknown', 'Yes', and 'No'. The 'No' option should be selected. The function checks the generated HTML against the expected output.
        
        Parameters:
        - widget: The widget instance to be tested.
        - field_name: The name of the field ('is_cool' in this case).
        - value: The value to
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
