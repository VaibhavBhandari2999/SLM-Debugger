from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of the `Input` widget with different attribute types.
        
        This function checks how the `Input` widget handles different attribute types, specifically focusing on the 'type' attribute. It tests the following scenarios:
        1. Sets the 'type' attribute to 'date' and verifies the HTML output.
        2. Reuses the same `attrs` dictionary for another `Input` widget and checks the HTML output.
        3. Modifies the 'type' attribute to 'number' and ensures that it
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
