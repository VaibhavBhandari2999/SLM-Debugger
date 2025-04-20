from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        self.check_html(self.widget, 'is_cool', True, html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_false(self):
        """
        Tests the rendering of a widget for the 'is_cool' field with a boolean value of False. The function checks if the rendered HTML matches the expected output.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function is used for asserting the correctness of the widget's rendering, hence it does not return any value.
        
        Key Elements:
        - `widget`: The widget instance being tested.
        - `is_cool`: The field name being rendered.
        - `
        """

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
        Tests the rendering of an unknown value for a boolean field in a dropdown select widget.
        
        This function checks the HTML output of the widget when the value for the 'is_cool' field is 'unknown'. The expected HTML output includes a select dropdown with options for 'Unknown', 'Yes', and 'No', where 'Unknown' is selected.
        
        Parameters:
        self: The instance of the test class.
        
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
        """
        Tests the rendering of a boolean field 'is_cool' with a value of '1'. The function checks if the rendered HTML matches the expected output. The expected HTML includes a select dropdown with three options: 'Unknown', 'Yes', and 'No'. The 'Unknown' option is selected by default, and the 'Yes' option is selected since the value '1' corresponds to 'true'.
        
        Parameters:
        - widget: The widget instance used for rendering the boolean field.
        - field_name:
        """

        self.check_html(self.widget, 'is_cool', '1', html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_2(self):
        """
        Tests the rendering of a boolean field value '2' for the 'is_cool' attribute. The function checks if the rendered HTML matches the expected output. The expected HTML includes a select dropdown with options for 'Unknown', 'Yes', and 'No', where 'Yes' is selected.
        
        Parameters:
        - widget: The widget object to be tested.
        - field_name: The name of the field ('is_cool' in this case).
        - value: The value to be rendered ('2'
        """

        self.check_html(self.widget, 'is_cool', '2', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_3(self):
        """
        Tests the rendering of a select widget for the 'is_cool' field with a value of '3'.
        The function checks that the rendered HTML matches the expected output.
        The expected HTML includes a select element with options for 'Unknown', 'Yes', and 'No',
        where 'No' is selected. The 'is_cool' field has a value of '3', which corresponds to the 'No' option.
        
        Parameters:
        - widget: The widget instance to be rendered.
        -
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
