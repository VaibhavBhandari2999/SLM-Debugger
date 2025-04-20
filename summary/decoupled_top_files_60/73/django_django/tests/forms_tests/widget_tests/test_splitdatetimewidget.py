from datetime import date, datetime, time

from django.forms import SplitDateTimeWidget

from .base import WidgetTest


class SplitDateTimeWidgetTest(WidgetTest):
    widget = SplitDateTimeWidget()

    def test_render_empty(self):
        """
        Tests the rendering of an empty date input field.
        
        This function checks the HTML output of the widget when rendering an empty date input field. The widget generates two input fields, one for each part of the date (day and month).
        
        Parameters:
        self (object): The test case object.
        
        Returns:
        None: This function asserts the expected HTML output against the actual output, hence no explicit return value is needed.
        
        Key Parameters:
        - `self`: The test case object used for assertions.
        
        Key
        """

        self.check_html(self.widget, 'date', '', html=(
            '<input type="text" name="date_0"><input type="text" name="date_1">'
        ))

    def test_render_none(self):
        self.check_html(self.widget, 'date', None, html=(
            '<input type="text" name="date_0"><input type="text" name="date_1">'
        ))

    def test_render_datetime(self):
        """
        Tests the rendering of a datetime object in a form widget.
        
        This function checks the HTML output of a form widget when rendering a datetime object. The datetime object is (2006, 1, 10, 7, 30), which corresponds to January 10, 2006, at 7:30 AM. The expected HTML output includes two input fields: one for the date and one for the time. The date field should have the value
        """

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
        """
        Tests the constructor attributes for the SplitDateTimeWidget.
        
        This function creates an instance of SplitDateTimeWidget with specified attributes and checks the HTML output for two input fields: one for the date and one for the time. The date and time values are provided as a datetime object, and the expected HTML output is verified.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        widget (SplitDateTimeWidget): The instance of the widget created for testing.
        attrs (dict): The dictionary containing the attributes
        """

        widget = SplitDateTimeWidget(attrs={'class': 'pretty'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=(
            '<input type="text" class="pretty" value="2006-01-10" name="date_0">'
            '<input type="text" class="pretty" value="07:30:00" name="date_1">'
        ))

    def test_constructor_different_attrs(self):
        """
        Test the constructor of the SplitDateTimeWidget with different attribute configurations.
        
        This function tests the constructor of the SplitDateTimeWidget by creating instances with various attribute configurations and validating the HTML output. The widget is expected to handle both date and time attributes separately or together.
        
        Parameters:
        None (The function uses instance attributes and methods to perform the tests).
        
        Returns:
        None (The function asserts the correctness of the HTML output using the check_html method).
        
        Key Attributes and Configurations:
        - `date_attrs`: A
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
