from datetime import date, datetime, time

from django.forms import SplitDateTimeWidget

from .base import WidgetTest


class SplitDateTimeWidgetTest(WidgetTest):
    widget = SplitDateTimeWidget()

    def test_render_empty(self):
        """
        Tests the rendering of an empty date input field.
        
        This function checks the HTML output of an empty date input field. The widget is expected to render two input fields, one for each part of the date (year and month). The generated HTML should match the provided template.
        
        Parameters:
        self (object): The test case object, which contains the widget to be tested.
        
        Returns:
        None: This function is a test case and does not return any value. It asserts that the rendered HTML matches the
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
        Tests the SplitDateTimeWidget's constructor with different attribute configurations.
        
        This function tests the SplitDateTimeWidget's constructor with various configurations of date and time attributes. It checks how the widget handles different combinations of date and time attributes and their values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `date_attrs`: A dictionary containing attributes for the date input field.
        - `time_attrs`: A dictionary containing attributes for the time input field.
        - `attrs`: A dictionary containing
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
