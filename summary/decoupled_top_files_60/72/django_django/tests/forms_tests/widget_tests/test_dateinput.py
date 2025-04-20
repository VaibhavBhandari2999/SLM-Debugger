from datetime import date

from django.forms import DateInput
from django.test import override_settings
from django.utils import translation

from .base import WidgetTest


class DateInputTest(WidgetTest):
    widget = DateInput()

    def test_render_none(self):
        self.check_html(self.widget, 'date', None, html='<input type="text" name="date">')

    def test_render_value(self):
        """
        Tests the rendering of a date value in a text input field.
        
        This function checks the rendering of a date object in a text input field. It uses the `check_html` method to ensure that the rendered HTML matches the expected output. The date is formatted as 'YYYY-MM-DD'.
        
        Parameters:
        - `d` (date): The date object to be rendered.
        
        Returns:
        None: This function does not return any value. It asserts the correctness of the rendered HTML.
        
        Example:
        >>>
        """

        d = date(2007, 9, 17)
        self.assertEqual(str(d), '2007-09-17')

        self.check_html(self.widget, 'date', d, html='<input type="text" name="date" value="2007-09-17">')
        self.check_html(self.widget, 'date', date(2007, 9, 17), html=(
            '<input type="text" name="date" value="2007-09-17">'
        ))

    def test_string(self):
        """
        Should be able to initialize from a string value.
        """
        self.check_html(self.widget, 'date', '2007-09-17', html=(
            '<input type="text" name="date" value="2007-09-17">'
        ))

    def test_format(self):
        """
        Use 'format' to change the way a value is displayed.
        """
        d = date(2007, 9, 17)
        widget = DateInput(format='%d/%m/%Y', attrs={'type': 'date'})
        self.check_html(widget, 'date', d, html='<input type="date" name="date" value="17/09/2007">')

    @override_settings(USE_L10N=True)
    @translation.override('de-at')
    def test_l10n(self):
        """
        Test localization of a date input field.
        
        This function checks the HTML output of a date input widget, ensuring that the date is correctly formatted according to the specified locale. The input widget is expected to render a date in the format 'DD.MM.YYYY'. The test case provides a specific date (2007-09-17) and expects the widget to render it as '17.09.2007'.
        
        Parameters:
        widget (Widget): The date input
        """

        self.check_html(
            self.widget, 'date', date(2007, 9, 17),
            html='<input type="text" name="date" value="17.09.2007">',
        )
