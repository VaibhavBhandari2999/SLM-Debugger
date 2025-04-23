from django.forms import Widget
from django.forms.widgets import Input

from .base import WidgetTest


class WidgetTests(WidgetTest):

    def test_format_value(self):
        """
        Tests the `format_value` method of the `Widget` class.
        
        This method is responsible for formatting the input value. It returns `None` for `None` or empty string inputs. For other inputs, it returns the value as is.
        
        Parameters:
        None (the method is tested for different input types)
        
        Returns:
        None or the input value (str or numeric)
        
        Test cases:
        - `format_value(None)` returns `None`
        - `format_value('')` returns `None`
        """

        widget = Widget()
        self.assertIsNone(widget.format_value(None))
        self.assertIsNone(widget.format_value(''))
        self.assertEqual(widget.format_value('español'), 'español')
        self.assertEqual(widget.format_value(42.5), '42.5')

    def test_value_omitted_from_data(self):
        widget = Widget()
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_no_trailing_newline_in_attrs(self):
        self.check_html(Input(), 'name', 'value', strict=True, html='<input type="None" name="name" value="value">')

    def test_attr_false_not_rendered(self):
        html = '<input type="None" name="name" value="value">'
        self.check_html(Input(), 'name', 'value', html=html, attrs={'readonly': False})
