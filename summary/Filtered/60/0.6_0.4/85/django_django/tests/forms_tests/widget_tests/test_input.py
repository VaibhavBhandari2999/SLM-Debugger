from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of the `Input` widget with different types of attributes.
        
        This function checks how the `Input` widget handles different attribute types, specifically focusing on the 'type' attribute. It verifies that the widget correctly renders the input element with the specified type and that changing the attribute after instantiation does not affect the widget's current state.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the `check_html` method to validate the HTML output of the `Input
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
