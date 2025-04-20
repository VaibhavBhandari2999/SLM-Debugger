from datetime import date, datetime, time

from django.forms import SplitDateTimeWidget

from .base import WidgetTest


class SplitDateTimeWidgetTest(WidgetTest):
    widget = SplitDateTimeWidget()

    def test_render_empty(self):
        self.check_html(self.widget, 'date', '', html=(
            '<input type="text" name="date_0"><input type="text" name="date_1">'
        ))

    def test_render_none(self):
        """
        Tests the rendering of a date widget with a None value.
        
        This function checks the HTML output of the widget when it is rendered with a None value for the 'date' field. The expected HTML consists of two input elements, one for each part of the date (year and month).
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - Widget: The date widget being tested.
        - Field: 'date'
        - Value: None
        - Expected HTML: Two input
        """

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
        """
        Tests the constructor attributes for the SplitDateTimeWidget.
        
        This function creates an instance of SplitDateTimeWidget with specified attributes and checks if the HTML output matches the expected format. The widget is initialized with a dictionary of attributes, including a 'class' attribute set to 'pretty'. The function then verifies that the generated HTML for the date and time inputs includes the specified class attribute.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes:
        widget (SplitDateTimeWidget): The instance of the widget created for
        """

        widget = SplitDateTimeWidget(attrs={'class': 'pretty'})
        self.check_html(widget, 'date', datetime(2006, 1, 10, 7, 30), html=(
            '<input type="text" class="pretty" value="2006-01-10" name="date_0">'
            '<input type="text" class="pretty" value="07:30:00" name="date_1">'
        ))

    def test_constructor_different_attrs(self):
        """
        Tests the behavior of the SplitDateTimeWidget with different attribute configurations.
        
        This function tests the SplitDateTimeWidget with various configurations of date and time attributes. It checks how the widget handles different combinations of date and time attributes and ensures that the widget correctly renders the input fields with the specified attributes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function creates instances of SplitDateTimeWidget with different attribute configurations.
        - It then checks the HTML output of the widget when rendering a datetime
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
