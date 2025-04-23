from django.forms import TextInput
from django.utils.safestring import mark_safe

from .base import WidgetTest


class TextInputTest(WidgetTest):
    widget = TextInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="text" name="email">')

    def test_render_none(self):
        self.check_html(self.widget, 'email', None, html='<input type="text" name="email">')

    def test_render_value(self):
        """
        Tests the rendering of a text input widget with the name 'email' and a value of 'test@example.com'. The function checks if the rendered HTML matches the expected output, which is an input element of type 'text' with the name 'email' and the specified value.
        
        Parameters:
        - widget: The widget instance to be rendered.
        - field: The name of the field (in this case, 'email').
        - value: The value to be set in the input field ('
        """

        self.check_html(self.widget, 'email', 'test@example.com', html=(
            '<input type="text" name="email" value="test@example.com">'
        ))

    def test_render_boolean(self):
        """
        Boolean values are rendered to their string forms ("True" and
        "False").
        """
        self.check_html(self.widget, 'get_spam', False, html=(
            '<input type="text" name="get_spam" value="False">'
        ))
        self.check_html(self.widget, 'get_spam', True, html=(
            '<input type="text" name="get_spam" value="True">'
        ))

    def test_render_quoted(self):
        self.check_html(
            self.widget, 'email', 'some "quoted" & ampersanded value',
            html='<input type="text" name="email" value="some &quot;quoted&quot; &amp; ampersanded value">',
        )

    def test_render_custom_attrs(self):
        self.check_html(
            self.widget, 'email', 'test@example.com', attrs={'class': 'fun'},
            html='<input type="text" name="email" value="test@example.com" class="fun">',
        )

    def test_render_unicode(self):
        """
        Tests the rendering of a widget with Unicode characters.
        
        This function checks the HTML output of a widget when it is rendered with a string containing Unicode characters. The widget is rendered with a specific name and a given set of Unicode characters. The test includes an HTML attribute for class styling. The expected HTML output is provided as a template, which includes the Unicode characters in their escaped form.
        
        Parameters:
        widget (Widget): The widget to be rendered.
        name (str): The name attribute of the input
        """

        self.check_html(
            self.widget, 'email', 'ŠĐĆŽćžšđ', attrs={'class': 'fun'},
            html=(
                '<input type="text" name="email" '
                'value="\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111" class="fun">'
            ),
        )

    def test_constructor_attrs(self):
        """
        Test the constructor attributes for a TextInput widget. The widget is initialized with a dictionary of attributes, including 'class' and 'type'. The function checks the generated HTML output for the widget with and without input values.
        
        Parameters:
        widget (TextInput): The TextInput widget instance with specified attributes.
        
        Returns:
        None: The function checks the HTML output and does not return any value.
        
        Key Parameters:
        - attrs (dict): A dictionary containing widget attributes such as 'class' and 'type'.
        
        Input
        """

        widget = TextInput(attrs={'class': 'fun', 'type': 'email'})
        self.check_html(widget, 'email', '', html='<input type="email" class="fun" name="email">')
        self.check_html(
            widget, 'email', 'foo@example.com',
            html='<input type="email" class="fun" value="foo@example.com" name="email">',
        )

    def test_attrs_precedence(self):
        """
        `attrs` passed to render() get precedence over those passed to the
        constructor
        """
        widget = TextInput(attrs={'class': 'pretty'})
        self.check_html(
            widget, 'email', '', attrs={'class': 'special'},
            html='<input type="text" class="special" name="email">',
        )

    def test_attrs_safestring(self):
        widget = TextInput(attrs={'onBlur': mark_safe("function('foo')")})
        self.check_html(widget, 'email', '', html='<input onBlur="function(\'foo\')" type="text" name="email">')

    def test_use_required_attribute(self):
        # Text inputs can safely trigger the browser validation.
        self.assertIs(self.widget.use_required_attribute(None), True)
        self.assertIs(self.widget.use_required_attribute(''), True)
        self.assertIs(self.widget.use_required_attribute('resume.txt'), True)
