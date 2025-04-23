from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Tests the rendering of a textarea widget with specified rows, columns, name, and value. The function compares the rendered HTML output against an expected HTML string.
        
        Parameters:
        widget (Widget): The widget instance to be rendered.
        field_name (str): The name of the field (e.g., 'msg').
        field_value (str): The value to be displayed in the textarea (e.g., 'value').
        
        Returns:
        None: The function asserts that the rendered HTML matches the expected
        """

        self.check_html(self.widget, 'msg', 'value', html=(
            '<textarea rows="10" cols="40" name="msg">value</textarea>'
        ))

    def test_render_required(self):
        """
        Tests the rendering of a required Textarea widget.
        
        This function checks if a Textarea widget renders correctly when the `is_required` attribute is set to True. The widget is expected to include the 'required' attribute in its HTML representation.
        
        Parameters:
        widget (Textarea): The Textarea widget to be tested.
        field (str): The name of the field (default is 'msg').
        value (str): The initial value of the field (default is 'value').
        
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
        self.check_html(self.widget, 'msg', 'some "quoted" & ampersanded value', html=(
            '<textarea rows="10" cols="40" name="msg">some &quot;quoted&quot; &amp; ampersanded value</textarea>'
        ))

    def test_mark_safe(self):
        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
