from django.forms import Textarea
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextareaTest(WidgetTest):
    widget = Textarea()

    def test_render(self):
        """
        Test the rendering of a widget with the specified name, value, and HTML output.
        
        Parameters:
        widget (Widget): The widget instance to be rendered.
        name (str): The name attribute for the textarea element.
        value (str): The initial value of the textarea.
        html (str): The expected HTML output of the rendered widget.
        
        This function checks if the rendered HTML of the widget matches the expected HTML output.
        """

        self.check_html(self.widget, 'msg', 'value', html=(
            '<textarea rows="10" cols="40" name="msg">value</textarea>'
        ))

    def test_render_required(self):
        """
        Tests the rendering of a required Textarea widget.
        
        This function checks if a Textarea widget, when marked as required, renders correctly with the appropriate HTML attributes. The widget's `is_required` attribute is set to `True` to indicate that the field is required. The function then uses a helper method `check_html` to verify that the rendered HTML matches the expected output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `widget`: The Textarea widget instance.
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
        Tests the behavior of the widget when rendering a marked-safe string. The function takes a widget instance, a field name, and a marked-safe string as input. It checks the HTML output of the widget for the specified field with the provided marked-safe string. The expected HTML output is also provided as a keyword argument 'html'.
        
        Parameters:
        - widget: The widget instance to test.
        - field_name: The name of the field for which the widget is rendering the marked-safe string.
        - mark_safe_string
        """

        self.check_html(self.widget, 'msg', mark_safe('pre &quot;quoted&quot; value'), html=(
            '<textarea rows="10" cols="40" name="msg">pre &quot;quoted&quot; value</textarea>'
        ))
