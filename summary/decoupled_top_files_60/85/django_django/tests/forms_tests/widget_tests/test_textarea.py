from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Tests the rendering of a textarea widget with specified rows, columns, name, and value. The function compares the rendered HTML output of the widget against an expected HTML string.
        
        Parameters:
        widget (Widget): The widget to be rendered.
        field (str): The name of the field (e.g., 'msg').
        value (str): The value to be displayed in the textarea (e.g., 'value').
        
        Returns:
        None: The function asserts that the rendered HTML matches the expected
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
        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        """
        Tests the behavior of the widget when rendering a marked-safe string. The function checks if the widget correctly renders the provided marked-safe string 'pre &quot;quoted&quot; value' in a textarea element. The expected HTML output is specified in the 'html' parameter.
        
        Parameters:
        - widget: The widget instance to be tested.
        - value: The marked-safe string to be rendered by the widget.
        
        Keyword Arguments:
        - html (str): The expected HTML output when the widget renders the
        """

        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
