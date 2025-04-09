"""
```markdown
This Python file contains tests for the `NullBooleanSelect` widget in Django. It includes various test cases to ensure the widget renders correctly under different input conditions and localizations.

#### Classes and Functions:
- **NullBooleanSelectTest**: A test class that inherits from `WidgetTest`. It defines several test methods to check how the `NullBooleanSelect` widget behaves with different input values.
  
#### Key Responsibilities:
- **test_render_true/test_render_false/test_render_none/test_render_value_***: These methods verify that the widget renders the correct option as selected based on the input value.
- **test_l10n**: This method checks that the widget's options are properly localized when the `USE_L10N` setting is
"""
from django.forms import NullBooleanSelect
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class NullBooleanSelectTest(WidgetTest):
    widget = NullBooleanSelect()

    def test_render_true(self):
        """
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true" selected>Yes</option>
        <option value="false">No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', True, html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_false(self):
        """
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true">Yes</option>
        <option value="false" selected>No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', False, html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true">Yes</option>
            <option value="false" selected>No</option>
            </select>"""
        ))

    def test_render_none(self):
        """
        <select name="is_cool">
        <option value="unknown" selected>Unknown</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', None, html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_unknown(self):
        """
        <select name="is_cool">
        <option value="unknown" selected>Unknown</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', 'unknown', html=(
            """<select name="is_cool">
            <option value="unknown" selected>Unknown</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_true(self):
        """
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true" selected>Yes</option>
        <option value="false">No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', 'true', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
            </select>"""
        ))

    def test_render_value_false(self):
        """
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true">Yes</option>
        <option value="false" selected>No</option>
        </select>
        """

        self.check_html(self.widget, 'is_cool', 'false', html=(
            """<select name="is_cool">
            <option value="unknown">Unknown</option>
            <option value="true">Yes</option>
            <option value="false" selected>No</option>
            </select>"""
        ))

    def test_render_value_1(self):
        """
        <select name="is_cool">
        <option value="unknown" selected>Unknown</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
        </select>
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
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true" selected>Yes</option>
        <option value="false">No</option>
        </select>
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
        <select name="is_cool">
        <option value="unknown">Unknown</option>
        <option value="true">Yes</option>
        <option value="false" selected>No</option>
        </select>
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
