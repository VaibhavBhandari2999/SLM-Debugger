from datetime import datetime

from django.forms import SplitHiddenDateTimeWidget
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class SplitHiddenDateTimeWidgetTest(WidgetTest):
    widget = SplitHiddenDateTimeWidget()

    def test_render_empty(self):
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
        """
        Tests the localization of a datetime object for a date input widget.
        
        This function checks the HTML output of a date input widget when given a datetime object. The datetime object is expected to have a day, month, year, hour, minute, and second. The function verifies that the HTML output correctly formats the date and time according to the specified locale, using a dot as the date separator and including the time in the format 'HH:MM:SS'.
        
        Parameters:
        - d (datetime): A
        """

        d = datetime(2007, 9, 17, 12, 51)
        self.check_html(self.widget, 'date', d, html=(
            """
            <input type="hidden" name="date_0" value="17.09.2007">
            <input type="hidden" name="date_1" value="12:51:00">
            """
        ))

    def test_constructor_different_attrs(self):
        """
        Tests the SplitHiddenDateTimeWidget constructor with different attribute configurations.
        
        This function tests the SplitHiddenDateTimeWidget constructor with various configurations of date and time attributes. It checks the widget's output for three different scenarios:
        1. When both date and time attributes are specified separately.
        2. When date attributes are specified in the date_attrs parameter and time attributes in the attrs parameter.
        3. When time attributes are specified in the time_attrs parameter and date attributes in the attrs parameter.
        
        Parameters:
        None
        
        Returns:
        """

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
