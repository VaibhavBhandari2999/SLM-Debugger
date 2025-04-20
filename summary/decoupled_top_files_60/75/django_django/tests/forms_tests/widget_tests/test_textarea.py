from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        self.check_html(self.widget, 'msg', 'value', html=(
            '<textarea rows="10" cols="40" name="msg">value</textarea>'
        ))

    def test_render_required(self):
        """
        Tests the rendering of a required Textarea widget.
        
        This function checks if a Textarea widget with the `is_required` attribute set to True is rendered correctly. The widget is expected to include the 'required' attribute in the HTML.
        
        Parameters:
        widget (Textarea): The Textarea widget to be tested.
        field_name (str): The name of the form field.
        initial_value (str): The initial value of the Textarea.
        
        Returns:
        None: This function asserts the correctness of
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
        Tests the escaping functionality of the widget for a textarea input.
        This function checks if the widget correctly escapes special characters in the provided message. The message contains quoted and ampersanded values. The expected HTML output is provided for validation.
        
        Parameters:
        self: The current instance of the class.
        
        Returns:
        None: This function is used for testing and does not return any value.
        
        Key Parameters:
        - widget: The widget instance to be tested.
        - name: The name attribute of the textarea
        """

        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
