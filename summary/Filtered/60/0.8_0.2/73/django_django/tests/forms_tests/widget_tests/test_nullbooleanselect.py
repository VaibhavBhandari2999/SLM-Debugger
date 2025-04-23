from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        Tests the rendering of a widget for the 'is_cool' field when the value is True. The function checks if the generated HTML matches the expected output.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function is used for asserting the correctness of the widget's rendering, hence it does not return any value.
        
        Key Elements:
        - `self.widget`: The widget instance to be tested.
        - `is_cool`: The field name being tested.
        - `True`:
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
        Tests the rendering of a boolean field 'is_cool' with a value of 'false'. The function checks the HTML output of the widget to ensure it correctly displays the options for 'is_cool' with 'false' selected.
        
        Parameters:
        - widget: The widget instance used for rendering the boolean field.
        - field_name: The name of the boolean field ('is_cool' in this case).
        - value: The value to be set for the boolean field ('false' in this case).
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
et = NullBooleanSelect()

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
