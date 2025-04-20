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
        """
        Test the rendering of a date input widget.
        
        This function tests the rendering of a date input widget for different datetime objects. It checks how the widget handles different datetime inputs and ensures that the rendered HTML matches the expected output.
        
        Parameters:
        - d (datetime): A datetime object with time and date information.
        - datetime (datetime): A datetime object with only date information.
        
        Returns:
        None: This function is used for testing and does not return any value. It checks the rendered HTML against expected
        """

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
        """
        Tests the behavior of the SplitHiddenDateTimeWidget with different attribute configurations.
        
        This function checks the SplitHiddenDateTimeWidget's constructor with various attribute configurations to ensure it correctly handles date and time inputs. The widget is instantiated with different combinations of date and time attributes, and the HTML output is validated against a predefined HTML string.
        
        Parameters:
        None (the function uses predefined inputs and outputs)
        
        Returns:
        None (the function asserts the correctness of the widget's output through internal checks)
        
        Key Attributes:
        -
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
