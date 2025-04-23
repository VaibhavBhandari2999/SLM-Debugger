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
        Tests rendering a widget with multiple email values.
        
        This function checks the HTML output of a widget when it is rendered with a list of email addresses. The expected HTML contains multiple hidden input fields, each representing one of the email addresses provided.
        
        Parameters:
        widget (Widget): The widget to be rendered.
        field_name (str): The name of the form field (e.g., 'email').
        values (list): A list of email addresses to be rendered.
        html (str): The expected
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
        Test the rendering of widget attributes.
        
        This function checks the HTML output of the widget when rendering a hidden input field for the 'email' field with a specific value and custom attributes. The expected HTML includes the name, value, and additional class attribute.
        
        Parameters:
        widget (Widget): The widget instance to be tested.
        name (str): The name of the input field (default is 'email').
        value (list): A list of values to be rendered in the input field (default is
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
