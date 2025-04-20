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
        """
        Tests the rendering of multiple email input fields.
        
        This function checks the rendering of multiple email input fields in the widget.
        It takes the widget, field name, and a list of email values as input and verifies
        that the rendered HTML matches the expected output. The expected HTML consists
        of multiple hidden input fields, each with a name corresponding to the field
        and a value from the provided list of email addresses.
        
        Parameters:
        widget (Widget): The widget to be tested.
        field_name (str
        """

        self.check_html(
            self.widget, 'email', ['test@example.com', 'foo@example.com'],
            html=(
                '<input type="hidden" name="email" value="test@example.com">\n'
                '<input type="hidden" name="email" value="foo@example.com">'
            ),
        )

    def test_render_attrs(self):
        """
        Test the rendering of input attributes.
        
        This function checks the rendering of a hidden input field for the 'email' field.
        It verifies that the input field is correctly rendered with the specified value and additional attributes.
        
        Parameters:
        widget (Widget): The widget instance to be tested.
        field_name (str): The name of the field ('email' in this case).
        value (list): The value to be set for the input field (['test@example.com'] in this case).
        attrs (
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

        )
