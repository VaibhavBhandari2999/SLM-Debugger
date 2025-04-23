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
        
        This function checks if a Textarea widget, when marked as required, is rendered with the appropriate HTML attributes. The widget is instantiated with the required attribute set to True. The function then uses a helper method to verify that the rendered HTML matches the expected output.
        
        Parameters:
        widget (Textarea): The Textarea widget instance to be tested.
        field_name (str): The name attribute for the textarea field.
        initial_value (str): The initial
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
        Tests the escaping functionality of the widget for a textarea input. The function checks if the widget generates the correct HTML output when provided with a string containing special characters such as quotes and ampersands. The input string is 'some "quoted" & ampersanded value'. The expected HTML output is a textarea element with the specified content, where special characters are properly escaped. The function uses the `check_html` method to validate the output.
        
        Parameters:
        - self: The test case instance.
        - widget
        """

        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
