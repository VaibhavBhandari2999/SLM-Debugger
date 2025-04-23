from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of the Input widget with different attribute types.
        
        This function checks the functionality of the Input widget with various attribute types. It creates an Input widget with specified attributes and verifies the HTML output. The function also demonstrates that changing the attribute value after creating the widget does not affect the widget's type.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates an Input widget with specified attributes.
        - Verifies the HTML output of the widget with the given attributes.
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
