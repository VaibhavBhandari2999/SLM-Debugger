"""
```markdown
# Summary

This file contains unit tests for Django form widgets. It includes tests for the `Widget` class's `format_value` method, which formats input values, and checks if a value is omitted from form data. Additionally, it verifies that certain attributes are not rendered in the HTML output.

## Classes and Functions

- **WidgetTests**: A test case class inheriting from `WidgetTest`.
  - **test_format_value**: Tests the `format_value` method of the `Widget` class.
  - **test_value_omitted_from_data**: Tests whether a value is omitted from form data.
  - **test_no_trailing_newline_in_attrs**: Ensures there are no trailing newlines in HTML attributes.
"""
from django.forms import Widget
from django.forms.widgets import Input

from .base import WidgetTest


class WidgetTests(WidgetTest):

    def test_format_value(self):
        """
        Tests the `format_value` method of the `Widget` class.
        
        - **Parameters:**
        - `self`: The instance of the `Widget` class being tested.
        
        - **Returns:**
        - None
        
        - **Behavior:**
        - Validates the behavior of the `format_value` method for different input types:
        - Returns `None` for `None` or empty string inputs.
        - Returns the input value unchanged for non-empty strings.
        - Returns the
        """

        widget = Widget()
        self.assertIsNone(widget.format_value(None))
        self.assertIsNone(widget.format_value(''))
        self.assertEqual(widget.format_value('español'), 'español')
        self.assertEqual(widget.format_value(42.5), '42.5')

    def test_value_omitted_from_data(self):
        """
        Tests whether a value is omitted from data.
        
        Args:
        data (dict): The form data.
        initial (dict): The initial data.
        name (str): The name of the field.
        
        Returns:
        bool: Whether the value is omitted from data.
        """

        widget = Widget()
        self.assertIs(widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)

    def test_no_trailing_newline_in_attrs(self):
        self.check_html(Input(), 'name', 'value', strict=True, html='<input type="None" name="name" value="value">')

    def test_attr_false_not_rendered(self):
        html = '<input type="None" name="name" value="value">'
        self.check_html(Input(), 'name', 'value', html=html, attrs={'readonly': False})
