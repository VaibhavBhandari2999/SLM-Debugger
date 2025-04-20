from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Tests the rendering of a textarea widget with specified rows, columns, name, and value. The function compares the rendered HTML output with an expected HTML string.
        
        Parameters:
        self (object): The test case object.
        widget (object): The textarea widget to be rendered.
        name (str): The name attribute of the textarea.
        value (str): The value to be set in the textarea.
        html (str): The expected HTML string representation of the rendered widget.
        
        Returns:
        None
        """

        self.check_html(self.widget, 'msg', 'value', html=(
            '<textarea rows="10" cols="40" name="msg">value</textarea>'
        ))

    def test_render_required(self):
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
        
        Args:
        self: The instance of the test class.
        field (str): The name of the field to be tested, in this case 'msg'.
        value (str): The value to be set in the textarea, including quoted and ampersanded text.
        html (str): The expected HTML output for the textarea element.
        
        This method checks that the widget correctly escapes the input value to prevent HTML injection or other security issues.
        """

        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
