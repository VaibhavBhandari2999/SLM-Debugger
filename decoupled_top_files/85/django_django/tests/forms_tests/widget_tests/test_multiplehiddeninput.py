"""
The provided Python file contains unit tests for the `MultipleHiddenInput` widget from Django's forms module. The `MultipleHiddenInputTest` class inherits from `WidgetTest` and includes several methods to test different scenarios involving the rendering of hidden input fields. These tests cover single and multiple values, custom attributes, and handling of empty and `None` values. The `check_html` method is used to validate the rendered HTML against expected outputs. The tests ensure that the `MultipleHiddenInput` widget correctly handles various configurations and attribute settings. ```python
"""
from django.forms import MultipleHiddenInput

from .base import WidgetTest


class MultipleHiddenInputTest(WidgetTest):
    widget = MultipleHiddenInput()

    def test_render_single(self):
        """
        Tests rendering a single email input field with the given value.
        
        Args:
        widget: The widget to be rendered.
        name: The name of the input field ('email' in this case).
        value: The value to be set in the input field (a list containing a single email address).
        
        Returns:
        A string representing the HTML code for the rendered input field.
        """

        self.check_html(
            self.widget, 'email', ['test@example.com'],
            html='<input type="hidden" name="email" value="test@example.com">',
        )

    def test_render_multiple(self):
        """
        Tests rendering multiple hidden inputs for the email field.
        
        Args:
        self: The instance of the test class.
        
        Summary:
        This function checks the HTML output of rendering multiple hidden inputs
        for the email field using the `check_html` method. It takes the widget,
        field name ('email'), and a list of email addresses as input. The expected
        HTML output is also provided as a string.
        
        Input:
        - widget: The widget object to be rendered.
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
        Tests rendering of form widget with specified attributes.
        
        Args:
        self: The instance of the test case class.
        
        Inputs:
        - widget: The form widget to be tested.
        - field_name: The name of the form field (e.g., 'email').
        - field_value: The value to be rendered in the widget (e.g., ['test@example.com']).
        - attrs: Additional attributes to be applied to the widget (e.g., {'class': 'fun'}
        """

        self.check_html(
            self.widget, 'email', ['test@example.com'], attrs={'class': 'fun'},
            html='<input type="hidden" name="email" value="test@example.com" class="fun">',
        )

    def test_render_attrs_multiple(self):
        """
        Tests rendering multiple hidden inputs with specified attributes.
        
        Args:
        self: The instance of the test case.
        
        Summary:
        This function checks the HTML output of rendering multiple hidden inputs with the given values and attributes. It uses the `check_html` method to compare the expected HTML with the actual rendered HTML.
        
        Inputs:
        - widget: The widget to be rendered.
        - field_name: The name of the field ('email' in this case).
        - values: A list of
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
        
        This function checks the HTML output of a MultipleHiddenInput widget with different configurations,
        including default attributes, single and multiple values, and overridden attributes.
        The `check_html` method is used to verify the generated HTML against expected outputs.
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
