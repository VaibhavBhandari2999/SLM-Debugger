"""
The provided Python file contains unit tests for a Django `TextInput` widget. It defines a class `TextInputTest` which inherits from `WidgetTest`. The class includes several test methods to verify the behavior of the `TextInput` widget under different conditions:

1. **Rendering with no value**: Ensures that the widget renders correctly without any input value.
2. **Rendering with `None` value**: Confirms that the widget handles `None` values appropriately.
3. **Rendering with a specific value**: Checks the rendering of the widget with a predefined value.
4. **Rendering boolean values**: Verifies how the widget handles boolean values by converting them to strings.
5. **Rendering quoted and ampersanded values**: Ensures that special characters in
"""
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
        Tests the rendering of an email input field with the given value.
        The function checks if the rendered HTML matches the expected output,
        using the `check_html` method of the widget. The input value is
        'test@example.com' and the expected HTML is an input element with
        type='text', name='email', and value='test@example.com'.
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
        """
        Tests the rendering of a text input widget with a quoted and ampersanded value.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        - Function: check_html
        - Input: widget, 'email', 'some "quoted" & ampersanded value'
        - Output: HTML string with escaped quotes and ampersands
        """

        self.check_html(
            self.widget, 'email', 'some "quoted" & ampersanded value',
            html='<input type="text" name="email" value="some &quot;quoted&quot; &amp; ampersanded value">',
        )

    def test_render_custom_attrs(self):
        """
        Tests rendering of custom attributes for the widget.
        
        This function checks the HTML output of the widget when rendering an input field
        with a specific value and custom attributes. The expected HTML is compared against
        the actual output to ensure correctness.
        
        Args:
        self: The instance of the test case class.
        
        Kwargs:
        widget: The widget instance to be tested.
        name: The name attribute of the input field.
        value: The value to be set in
        """

        self.check_html(
            self.widget, 'email', 'test@example.com', attrs={'class': 'fun'},
            html='<input type="text" name="email" value="test@example.com" class="fun">',
        )

    def test_render_unicode(self):
        """
        Tests rendering of a widget with Unicode input.
        
        This function checks the HTML output of a widget when rendering an input
        value containing Unicode characters. The widget is expected to handle
        these characters correctly and include them in the rendered HTML.
        
        Args:
        self: The instance of the test case class.
        
        Keyword Args:
        widget: The widget to be tested.
        field_name (str): The name of the form field.
        input_value (str): The Unicode string to be
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
        Tests the constructor of the TextInput widget. Verifies that the widget correctly handles attributes such as 'class' and 'type'. The widget is instantiated with a dictionary of attributes and produces the expected HTML output when rendered with or without input values.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Called:
        - `check_html`: Compares the generated HTML output of the widget with the expected HTML string.
        
        Attributes Set:
        - `attrs`: A dictionary containing widget attributes like
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
        """
        Tests the `use_required_attribute` method of the widget.
        
        This method checks if the widget uses required attributes for text inputs,
        regardless of whether the input is `None`, an empty string, or a file name.
        The method returns `True` for all cases, indicating that required attributes
        are always used.
        
        Args:
        value (str): The input value to check.
        
        Returns:
        bool: Whether the required attribute is used for the given input.
        """

        # Text inputs can safely trigger the browser validation.
        self.assertIs(self.widget.use_required_attribute(None), True)
        self.assertIs(self.widget.use_required_attribute(''), True)
        self.assertIs(self.widget.use_required_attribute('resume.txt'), True)
