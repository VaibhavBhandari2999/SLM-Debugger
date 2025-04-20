from django.forms import Widget
from django.forms.widgets import Input

from .base import WidgetTest


class WidgetTests(WidgetTest):

    def test_format_value(self):
        """
        Tests the format_value method of the Widget class.
        
        This method is responsible for formatting the input value. It returns None for None or empty string inputs, and returns the input value as is for other types.
        
        Parameters:
        None
        
        Returns:
        None or the input value as is.
        
        Test Cases:
        - format_value(None): Returns None
        - format_value(''): Returns None
        - format_value('español'): Returns 'español'
        - format_value(42.5): Returns
        """

        widget = Widget()
        self.assertIsNone(widget.format_value(None))
        self.assertIsNone(widget.format_value(''))
        self.assertEqual(widget.format_value('español'), 'español')
        self.assertEqual(widget.format_value(42.5), '42.5')

    def test_value_omitted_from_data(self):
        """
        Tests the `value_omitted_from_data` method of a Widget.
        
        This method checks whether the value for a specific field is omitted from the data.
        
        Parameters:
        data (dict): The form data.
        files (dict): The form files.
        name (str): The name of the field to check.
        
        Returns:
        bool: True if the value is omitted, False otherwise.
        
        Example Usage:
        >>> widget = Widget()
        >>> widget.value_omitted_from_data({}, {}, '
        """

        widget = Widget()
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_no_trailing_newline_in_attrs(self):
        self.check_html(Input(), 'name', 'value', strict=True, html='<input type="None" name="name" value="value">')

    def test_attr_false_not_rendered(self):
        html = '<input type="None" name="name" value="value">'
        self.check_html(Input(), 'name', 'value', html=html, attrs={'readonly': False})
