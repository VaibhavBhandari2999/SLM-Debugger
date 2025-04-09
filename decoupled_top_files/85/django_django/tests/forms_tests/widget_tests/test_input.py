"""
```markdown
This Python script contains tests for Django form input widgets. Specifically, it focuses on verifying the behavior of input widgets when different attribute types are used, particularly the 'type' attribute. The `InputTests` class inherits from `WidgetTest` and includes a single test method, `test_attrs_with_type`, which checks how input widgets handle various attribute types without altering their previous state.

#### Classes Defined:
- **InputTests**: A test case class for input widgets, inheriting from `WidgetTest`.

#### Functions Defined:
- **test_attrs_with_type**: A test function that verifies the handling of different attribute types by input widgets.

#### Key Responsibilities:
- Ensures that input widgets correctly interpret and render different attribute types, especially the '
"""
from django.forms.widgets import Input

from .base import WidgetTest


class InputTests(WidgetTest):

    def test_attrs_with_type(self):
        """
        Tests the behavior of input widgets with different attribute types.
        
        This function checks how input widgets handle different attribute types,
        specifically focusing on the 'type' attribute. It creates an input widget
        with initial attributes and verifies its HTML output. The function then
        reuses the same attributes for another widget and ensures that changing
        the 'type' attribute does not alter the previously created widget's output.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        """

        attrs = {'type': 'date'}
        widget = Input(attrs)
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
        # reuse the same attrs for another widget
        self.check_html(Input(attrs), 'name', 'value', '<input type="date" name="name" value="value">')
        attrs['type'] = 'number'  # shouldn't change the widget type
        self.check_html(widget, 'name', 'value', '<input type="date" name="name" value="value">')
