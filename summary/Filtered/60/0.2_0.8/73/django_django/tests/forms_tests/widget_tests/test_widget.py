from django.forms import Widget
from django.forms.widgets import Input

from .base import WidgetTest


class WidgetTests(WidgetTest):

    def test_format_value(self):
        widget = Widget()
        self.assertIsNone(widget.format_value(None))
        self.assertIsNone(widget.format_value(''))
        self.assertEqual(widget.format_value('español'), 'español')
        self.assertEqual(widget.format_value(42.5), '42.5')

    def test_value_omitted_from_data(self):
        """
        Tests the `value_omitted_from_data` method of a Widget.
        
        Parameters:
        - widget (Widget): The Widget instance to test.
        
        Returns:
        - None: This function does not return any value. It asserts the correctness of the `value_omitted_from_data` method.
        
        Key Parameters:
        - widget: The Widget instance being tested.
        - data (dict): The data dictionary passed to the method.
        - files (dict): The files dictionary passed to the method.
        - name (str):
        """

        widget = Widget()
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_no_trailing_newline_in_attrs(self):
        self.check_html(Input(), 'name', 'value', strict=True, html='<input type="None" name="name" value="value">')

    def test_attr_false_not_rendered(self):
        html = '<input type="None" name="name" value="value">'
        self.check_html(Input(), 'name', 'value', html=html, attrs={'readonly': False})
t(), 'name', 'value', html=html, attrs={'readonly': False})
