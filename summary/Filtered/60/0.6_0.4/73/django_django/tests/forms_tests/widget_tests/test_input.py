from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of the `Input` widget with different attribute types.
        
        This function checks how the `Input` widget handles different attribute types, specifically focusing on the 'type' attribute. It creates an `attrs` dictionary with the 'type' key and tests the widget's HTML output with this attribute. The function also verifies that changing the 'type' attribute in the dictionary does not affect the widget's previous state.
        
        Parameters:
        - None (This function uses internal attributes and does not take any parameters
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
