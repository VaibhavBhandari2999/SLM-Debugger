from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Tests the rendering of a textarea widget.
        
        This function checks the HTML output of a textarea widget. It expects the widget to be rendered with specific attributes and content.
        
        Parameters:
        widget (Widget): The widget to be rendered.
        field_name (str): The name of the field (e.g., 'msg').
        field_value (str): The value to be displayed in the textarea (e.g., 'value').
        
        Returns:
        None: This function is used for assertion and does not return
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
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
