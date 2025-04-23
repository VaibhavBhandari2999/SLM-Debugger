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
        
        This function checks if a Textarea widget renders correctly when the `is_required` attribute is set to True. The widget is expected to include the 'required' attribute in the HTML output.
        
        Parameters:
        widget (Textarea): The Textarea widget instance to be tested.
        field_name (str): The name of the field (default is 'msg').
        initial_value (str): The initial value of the field (default is 'value').
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
        """
        Tests the behavior of the widget when rendering a marked-safe string. The function checks if the widget correctly handles and renders a string that has been marked as safe using Django's mark_safe function. The input parameters are:
        - `self`: The test case instance.
        - `widget`: The widget to be tested.
        - `value`: The marked-safe string to be rendered by the widget.
        The expected output is a properly formatted HTML textarea element that includes the marked-safe string without being escaped.
        
        :param widget:
        """

        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
