from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of the Input widget with different types of attributes.
        
        This function checks how the Input widget handles different attribute types, specifically focusing on the 'type' attribute. It verifies that the widget correctly renders the input type based on the provided attribute and ensures that changing the attribute after initialization does not affect the widget's state.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a dictionary `attrs` to define the attributes for the Input widget, with a key '
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
