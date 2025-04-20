from django.forms import MultipleHiddenInput

from .base import WidgetTest


class MultipleHiddenInputTest(WidgetTest):
    widget = MultipleHiddenInput()

    def test_render_single(self):
        """
        Tests the rendering of a single email input field.
        
        This function checks the HTML output of the widget when rendering a single email input field. It expects the widget to generate a hidden input element with the name 'email' and the provided value.
        
        Parameters:
        self (object): The test case object.
        field_name (str): The name of the input field, in this case 'email'.
        value (list): A list containing the value to be rendered in the input field, here ['test
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
        self.check_html(
            self.widget, 'email', ['test@example.com'], attrs={'class': 'fun'},
            html='<input type="hidden" name="email" value="test@example.com" class="fun">',
        )

    def test_render_attrs_multiple(self):
        """
        Test rendering of multiple hidden input fields with specified attributes.
        
        This function checks the rendering of multiple hidden input fields for the 'email' field with the provided values and attributes. It ensures that the generated HTML matches the expected output.
        
        Parameters:
        widget (Widget): The widget instance to be rendered.
        name (str): The name of the input field (default: 'email').
        value (list): A list of values for the input fields (default: ['test@example.com', 'foo@example
        """

        self.check_html(
            self.widget, 'email', ['test@example.com', 'foo@example.com'], attrs={'class': 'fun'},
            html=(
                '<input type="hidden" name="email" value="test@example.com" class="fun">\n'
                '<input type="hidden" name="email" value="foo@example.com" class="fun">'
            ),
        )

    def test_render_attrs_constructor(self):
        """
        Test the rendering of a MultipleHiddenInput widget with various attributes and values.
        
        This function checks the rendering of a MultipleHiddenInput widget with different attributes and input values. It verifies that the widget correctly handles a single value, multiple values, and custom attributes.
        
        Parameters:
        - widget: The MultipleHiddenInput widget to be tested.
        - field_name: The name of the form field.
        - field_values: A list of values to be rendered in the widget.
        - attrs: Additional attributes to be applied to
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
