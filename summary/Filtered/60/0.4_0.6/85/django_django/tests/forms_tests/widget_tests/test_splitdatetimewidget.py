from datetime import date, datetime, time

from django.forms import SplitDateTimeWidget

from .base import WidgetTest


class SplitDateTimeWidgetTest(WidgetTest):
    widget = SplitDateTimeWidget()

    def test_render_empty(self):
        """
        Tests the rendering of an empty date input field.
        
        This function checks the HTML output of an empty date input field. The widget is expected to generate two input elements, one for each part of the date (day and month). The function uses a predefined check_html method to validate the generated HTML against the expected output.
        
        Parameters:
        widget (Widget): The widget instance to be rendered.
        field (str): The name of the field to be rendered, in this case 'date'.
        value (
        """

        self.check_html(self.widget, 'date', '', html=(
            '<input type="text" name="date_0"><input type="text" name="date_1">'
        ))

    def test_render_none(self):
        self.check_html(self.widget, 'date', None, html=(
            '<input type="text" name="date_0"><input type="text" name="date_1">'
        ))

    def test_render_datetime(self):
        self.check_html(self.widget, 'date', datetime(2006, 1, 10, 7, 30), html=(
            '<input type="text" name="date_0" value="2006-01-10">'
            '<input type="text" name="date_1" value="07:30:00">'
        ))

    def test_render_date_and_time(self):
        self.check_html(self.widget, 'date', [date(2006, 1, 10), time(7, 30)], html=(
            '<input type="text" name="date_0" value="2006-01-10">'
            '<input type="text" name="date_1" value="07:30:00">'
        ))

    def test_constructor_attrs(self):
        widget = SplitDateTimeWidget(attrs={'class': 'pretty'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=(
            '<input type="text" class="pretty" value="2006-01-10" name="date_0">'
            '<input type="text" class="pretty" value="07:30:00" name="date_1">'
        ))

    def test_constructor_different_attrs(self):
        """
        Tests the SplitDateTimeWidget constructor with different attribute configurations.
        
        This function tests the SplitDateTimeWidget constructor with various attribute configurations to ensure that the widget correctly handles different attribute settings for date and time inputs. The constructor is tested with the following scenarios:
        - Separate date and time attribute configurations.
        - Date attribute configuration with a different set of attributes for time.
        - Time attribute configuration with a different set of attributes for date.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        The function uses the `check_html`
        """

        html = (
            '<input type="text" class="foo" value="2006-01-10" name="date_0">'
            '<input type="text" class="bar" value="07:30:00" name="date_1">'
        )
        widget = SplitDateTimeWidget(date_attrs={'class': 'foo'}, time_attrs={'class': 'bar'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)
        widget = SplitDateTimeWidget(date_attrs={'class': 'foo'}, attrs={'class': 'bar'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)
        widget = SplitDateTimeWidget(time_attrs={'class': 'bar'}, attrs={'class': 'foo'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=html)

    def test_formatting(self):
        """
        Use 'date_format' and 'time_format' to change the way a value is
        displayed.
        """
        widget = SplitDateTimeWidget(
            date_format='%d/%m/%Y', time_format='%H:%M',
        )
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=(
            '<input type="text" name="date_0" value="10/01/2006">'
            '<input type="text" name="date_1" value="07:30">'
        ))
