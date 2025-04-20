from datetime import datetime

from django.forms import DateTimeInput
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class DateTimeInputTest(WidgetTest):
    widget = DateTimeInput()

    def test_render_none(self):
        self.check_html(self.widget, 'date', None, '<input type="text" name="date">')

    def test_render_value(self):
        """
        The microseconds are trimmed on display, by default.
        """
        d = datetime(2007, 9, 17, 12, 51, 34, 482548)
        self.assertEqual(str(d), '2007-09-17 12:51:34.482548')
        self.check_html(self.widget, 'date', d, html=(
            '<input type="text" name="date" value="2007-09-17 12:51:34">'
        ))
        self.check_html(self.widget, 'date', datetime(2007, 9, 17, 12, 51, 34), html=(
            '<input type="text" name="date" value="2007-09-17 12:51:34">'
        ))
        self.check_html(self.widget, 'date', datetime(2007, 9, 17, 12, 51), html=(
            '<input type="text" name="date" value="2007-09-17 12:51:00">'
        ))

    def test_render_formatted(self):
        """
        Use 'format' to change the way a value is displayed.
        """
        widget = DateTimeInput(
            format='%d/%m/%Y %H:%M', attrs={'type': 'datetime'},
        )
        d = datetime(2007, 9, 17, 12, 51, 34, 482548)
        self.check_html(widget, 'date', d, html='<input type="datetime" name="date" value="17/09/2007 12:51">')

    @override_settings(USE_L10N=True)
    @translation.override('de-at')
    def test_l10n(self):
        """
        Test localization of a date input widget.
        
        This function tests the localization of a date input widget by setting a specific datetime object and verifying the generated HTML output. The datetime object is formatted according to the locale settings, and the expected HTML is provided for comparison.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `d`: A `datetime` object representing the date and time to be set in the widget.
        
        Keywords:
        - `self`: The test case instance.
        
        Expected Input
        """

        d = datetime(2007, 9, 17, 12, 51, 34, 482548)
        self.check_html(self.widget, 'date', d, html=(
            '<input type="text" name="date" value="17.09.2007 12:51:34">'
        ))

    @override_settings(USE_L10N=True)
    @translation.override('de-at')
    def test_locale_aware(self):
        """
        Test the date input widget in different settings and locales.
        
        This function tests the behavior of the date input widget under different configurations and locales. It checks how the widget handles date formatting when USE_L10N is set to False and when the language is set to Spanish ('es').
        
        Parameters:
        - d (datetime): The datetime object to be tested.
        
        Returns:
        - None: The function asserts the expected HTML output for the given datetime object under different settings and locales.
        
        Key Points:
        - When USE
        """

        d = datetime(2007, 9, 17, 12, 51, 34, 482548)
        with self.settings(USE_L10N=False):
            self.check_html(
                self.widget, 'date', d,
                html='<input type="text" name="date" value="2007-09-17 12:51:34">',
            )
        with translation.override('es'):
            self.check_html(
                self.widget, 'date', d,
                html='<input type="text" name="date" value="17/09/2007 12:51:34">',
            )
