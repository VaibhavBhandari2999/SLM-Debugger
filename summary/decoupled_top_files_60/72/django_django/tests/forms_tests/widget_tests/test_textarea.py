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
        
        This function checks the HTML output of a Textarea widget when the 'is_required' attribute is set to True. The widget is rendered with the specified name and value, and the resulting HTML is compared against an expected output.
        
        Parameters:
        widget (Textarea): The Textarea widget to be rendered.
        field_name (str): The name attribute of the textarea.
        field_value (str): The value to be set in the textarea.
        
        Returns:
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
        Test the escaping functionality of the widget.
        
        This function checks if the widget correctly escapes special characters in the provided message. The message is expected to contain double quotes and ampersands, which should be properly escaped in the HTML output.
        
        Parameters:
        self (object): The instance of the test case class.
        message (str): The message to be displayed in the textarea, containing special characters that need to be escaped.
        
        Returns:
        None: This function is a test case and does not return any
        """

        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
