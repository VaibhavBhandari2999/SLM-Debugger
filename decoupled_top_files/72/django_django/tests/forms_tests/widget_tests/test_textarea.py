"""
The provided Python file is part of a Django application's testing suite, specifically focusing on the `Textarea` widget from Django's forms module. It includes several test cases to ensure that the `Textarea` widget behaves as expected under various conditions.

#### Classes and Functions Defined:
- **TextareaTest**: A subclass of `WidgetTest` that tests the `Textarea` widget.
  - **test_render**: Tests the rendering of a `Textarea` widget with specified rows, columns, name, and value.
  - **test_render_required**: Tests the rendering of a `Textarea` widget when it is marked as required.
  - **test_render_empty**: Tests the rendering of a `Textarea` widget with an empty value.
  - **test_render_none
"""
from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Tests the rendering of a textarea widget with specified rows, columns, name, and value. The function checks if the rendered HTML matches the expected output.
        
        Args:
        self: The instance of the class containing the widget to be tested.
        
        Keyword Args:
        widget: The textarea widget to be rendered.
        field_name (str): The name attribute of the textarea.
        field_value (str): The value to be set in the textarea.
        html (str): The expected HTML representation of
        """

        self.check_html(self.widget, 'msg', 'value', html=(
            '<textarea rows="10" cols="40" name="msg">value</textarea>'
        ))

    def test_render_required(self):
        """
        Tests the rendering of a required Textarea widget.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the rendering of a required Textarea widget by setting the `is_required` attribute to True and checking the generated HTML output using the `check_html` method.
        
        Important Functions:
        - `Textarea()`: Creates an instance of the Textarea widget.
        - `widget.is_required = True`: Sets the `is_required` attribute to True.
        """

        widget = Textarea()
        widget.is_required = True
        self.check_html(widget, 'msg', 'value', html='<textarea rows="10" cols="40" name="msg">value</textarea>')

    def test_render_empty(self):
        self.check_html(self.widget, 'msg', '', html='<textarea rows="10" cols="40" name="msg"></textarea>')

    def test_render_none(self):
        self.check_html(self.widget, 'msg', None, html='<textarea rows="10" cols="40" name="msg"></textarea>')

    def test_escaping(self):
        """
        Tests escaping of special characters in a textarea widget.
        
        Args:
        self: The instance of the class containing this method.
        
        Summary:
        This function checks the HTML output of a textarea widget with the given message, ensuring that special characters are properly escaped. The message contains double quotes and an ampersand, which should be converted to their corresponding HTML entities (&quot; and &amp;) in the output.
        
        Input:
        - `self`: The instance of the class.
        - `
        """

        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        """
        Tests the rendering of a textarea widget with a marked safe string. The function checks if the widget correctly renders the provided marked safe string as HTML, ensuring that special characters are properly escaped and displayed. The input is a marked safe string, and the expected output is a properly formatted HTML textarea element.
        
        Args:
        self: The instance of the class containing this method.
        
        Keyword Args:
        field_name (str): The name of the form field.
        value (str): The marked safe string
        """

        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
