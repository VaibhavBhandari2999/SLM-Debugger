from django.forms import MultipleHiddenInput

from .base import WidgetTest


class MultipleHiddenInputTest(WidgetTest):
    widget = MultipleHiddenInput()

    def test_render_single(self):
        """
        Tests the rendering of a single email input field.
        This function checks the HTML output of the widget when rendering a single email input field with the name 'email' and the value 'test@example.com'. The expected HTML is a hidden input field with the specified name and value.
        
        Parameters:
        widget (Widget): The widget to be tested.
        field_name (str): The name of the input field (default is 'email').
        value (list): A list containing the value to be rendered in
        """

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
        
        This function checks the HTML output of the widget when rendering a hidden input field for the 'email' field with a specific value and custom attributes. The expected HTML includes the name, value, and additional class attribute.
        
        Parameters:
        widget (Widget): The widget instance to be tested.
        field_name (str): The name of the field to be rendered (default is 'email').
        value (list): The value(s) to be set for the input field
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
        Tests the `render` method of the `MultipleHiddenInput` widget.
        
        This function checks the rendering of a `MultipleHiddenInput` widget with various attributes and input values. It ensures that the widget correctly handles multiple hidden inputs and applies the specified attributes to each input.
        
        Parameters:
        - widget: The `MultipleHiddenInput` widget instance to be tested.
        - field_name: The name of the form field.
        - values: A list of values to be rendered in the hidden inputs.
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
          ),
        )
