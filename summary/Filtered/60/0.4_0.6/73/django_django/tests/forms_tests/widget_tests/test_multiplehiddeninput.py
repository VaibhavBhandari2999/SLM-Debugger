from django.forms import MultipleHiddenInput

from .base import WidgetTest


class MultipleHiddenInputTest(WidgetTest):
    widget = MultipleHiddenInput()

    def test_render_single(self):
        self.check_html(
            self.widget, 'email', ['test@example.com'],
            html='<input type="hidden" name="email" value="test@example.com">',
        )

    def test_render_multiple(self):
        self.check_html(
            self.widget, 'email', ['test@example.com', 'foo@example.com'],
            html=(
                '<input type="hidden" name="email" value="test@example.com">\n'
                '<input type="hidden" name="email" value="foo@example.com">'
            ),
        )

    def test_render_attrs(self):
        """
        Tests the rendering of widget attributes.
        
        This function checks the HTML output of the widget when rendering a hidden input field for the 'email' field with a specified value and additional attributes. The function expects the widget to generate an HTML input element with the correct name, value, and additional class attribute.
        
        Parameters:
        widget (Widget): The widget instance to test.
        field_name (str): The name of the field to render (default is 'email').
        value (list): The value to be
        """

        self.check_html(
            self.widget, 'email', ['test@example.com'], attrs={'class': 'fun'},
            html='<input type="hidden" name="email" value="test@example.com" class="fun">',
        )

    def test_render_attrs_multiple(self):
        self.check_html(
            self.widget, 'email', ['test@example.com', 'foo@example.com'], attrs={'class': 'fun'},
            html=(
                '<input type="hidden" name="email" value="test@example.com" class="fun">\n'
                '<input type="hidden" name="email" value="foo@example.com" class="fun">'
            ),
        )

    def test_render_attrs_constructor(self):
        """
        Tests the `render_attrs` constructor for the `MultipleHiddenInput` widget.
        
        This function checks the rendering of attributes for a `MultipleHiddenInput` widget.
        It verifies that the widget correctly handles a single value, multiple values, and custom attributes.
        
        Parameters:
        - widget: The `MultipleHiddenInput` widget instance to be tested.
        - field_name: The name of the form field.
        - values: A list of values to be rendered in the widget.
        - attrs: Additional
        """

        widget = MultipleHiddenInput(attrs={'class': 'fun'})
        self.check_html(widget, 'email', [], '')
        self.check_html(
            widget, 'email', ['foo@example.com'],
            html='<input type="hidden" class="fun" value="foo@example.com" name="email">',
        )
        self.check_html(
            widget, 'email', ['foo@example.com', 'test@example.com'],
            html=(
                '<input type="hidden" class="fun" value="foo@example.com" name="email">\n'
                '<input type="hidden" class="fun" value="test@example.com" name="email">'
            ),
        )
        self.check_html(
            widget, 'email', ['foo@example.com'], attrs={'class': 'special'},
            html='<input type="hidden" class="special" value="foo@example.com" name="email">',
        )

    def test_render_empty(self):
        self.check_html(self.widget, 'email', [], '')

    def test_render_none(self):
        self.check_html(self.widget, 'email', None, '')

    def test_render_increment_id(self):
        """
        Each input should get a separate ID.
        """
        self.check_html(
            self.widget, 'letters', ['a', 'b', 'c'], attrs={'id': 'hideme'},
            html=(
                '<input type="hidden" name="letters" value="a" id="hideme_0">\n'
                '<input type="hidden" name="letters" value="b" id="hideme_1">\n'
                '<input type="hidden" name="letters" value="c" id="hideme_2">'
            ),
        )
