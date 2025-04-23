from django.forms import Widget
from django.forms.widgets import Input

from .base import WidgetTest


class WidgetTests(WidgetTest):

    def test_format_value(self):
        """
        Tests the format_value method of the Widget class.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - value: The value to be formatted by the widget.
        
        Keywords:
        - None
        
        Details:
        - If the input value is None or an empty string, the method returns None.
        - If the input value is a string, it is returned as is.
        - If the input value is a number, it is returned as a string.
        """

        widget = Widget()
        self.assertIsNone(widget.format_value(None))
        self.assertIsNone(widget.format_value(''))
        self.assertEqual(widget.format_value('español'), 'español')
        self.assertEqual(widget.format_value(42.5), '42.5')

    def test_value_omitted_from_data(self):
        """
        test_value_omitted_from_data
        
        This function tests whether a value is omitted from data for a given widget field.
        
        Parameters:
        data (dict): The dictionary containing the data.
        initial (dict): The dictionary containing the initial state of the widget.
        name (str): The name of the widget field to check.
        
        Returns:
        bool: True if the value is omitted from data, False otherwise.
        """

        widget = Widget()
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_no_trailing_newline_in_attrs(self):
        self.check_html(Input(), 'name', 'value', strict=True, html='<input type="None" name="name" value="value">')

    def test_attr_false_not_rendered(self):
        html = '<input type="None" name="name" value="value">'
        self.check_html(Input(), 'name', 'value', html=html, attrs={'readonly': False})
