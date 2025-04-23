from datetime import datetime

from django.forms import SplitHiddenDateTimeWidget
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class SplitHiddenDateTimeWidgetTest(WidgetTest):
    widget = SplitHiddenDateTimeWidget()

    def test_render_empty(self):
        """
        Tests the rendering of an empty date field.
        
        This function checks the HTML output of a date widget when the value is an empty string. It ensures that the widget correctly renders two hidden input fields, one for each part of the date (year and month).
        
        Parameters:
        self (object): The test case object, used to call the widget and check the HTML output.
        
        Returns:
        None: This function is a test case and does not return any value. It asserts that the generated HTML matches the
        """

        self.check_html(self.widget, 'date', '', html=(
            '<input type="hidden" name="date_0"><input type="hidden" name="date_1">'
        ))

    def test_render_value(self):
        d = datetime(2007, 9, 17, 12, 51, 34, 482548)
        self.check_html(self.widget, 'date', d, html=(
            '<input type="hidden" name="date_0" value="2007-09-17">'
            '<input type="hidden" name="date_1" value="12:51:34">'
        ))
        self.check_html(self.widget, 'date', datetime(2007, 9, 17, 12, 51, 34), html=(
            '<input type="hidden" name="date_0" value="2007-09-17">'
            '<input type="hidden" name="date_1" value="12:51:34">'
        ))
        self.check_html(self.widget, 'date', datetime(2007, 9, 17, 12, 51), html=(
            '<input type="hidden" name="date_0" value="2007-09-17">'
            '<input type="hidden" name="date_1" value="12:51:00">'
        ))

    @override_settings(USE_L10N=True)
    @translation.override('de-at')
    def test_l10n(self):
        d = datetime(2007, 9, 17, 12, 51)
        self.check_html(self.widget, 'date', d, html=(
            """
            <input type="hidden" name="date_0" value="17.09.2007">
            <input type="hidden" name="date_1" value="12:51:00">
            """
        ))

    def test_constructor_different_attrs(self):
        html = (
            '<input type="hidden" class="foo" value="2006-01-10" name="date_0">'
            '<input type="hidden" class="bar" value="07:30:00" name="date_1">'
        )
        widget = SplitHiddenDateTimeWidget(date_attrs={'class': 'foo'}, time_attrs={'class': 'bar'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)
        widget = SplitHiddenDateTimeWidget(date_attrs={'class': 'foo'}, attrs={'class': 'bar'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)
        widget = SplitHiddenDateTimeWidget(time_attrs={'class': 'bar'}, attrs={'class': 'foo'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)
