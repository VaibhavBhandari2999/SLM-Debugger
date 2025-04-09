"""
The provided Python file contains unit tests for the `CheckboxInput` widget from Django's forms framework. It defines a test class `CheckboxInputTest` that inherits from `WidgetTest`, a base class for testing form widgets. The class includes several test methods to verify the behavior of the `CheckboxInput` widget under different conditions:

1. **Rendering Empty and None Values**: Tests how the widget renders when the value is empty or `None`.
2. **Rendering Boolean Values**: Verifies the rendering of the widget when the value is `False`, `True`, or any other boolean-like value.
3. **Handling Non-Boolean Values**: Ensures that non-boolean values (like strings or integers) are correctly rendered.
4. **Custom
"""
from django.forms import CheckboxInput

from .base import WidgetTest


class CheckboxInputTest(WidgetTest):
    widget = CheckboxInput()

    def test_render_empty(self):
        self.check_html(self.widget, 'is_cool', '', html='<input type="checkbox" name="is_cool">')

    def test_render_none(self):
        self.check_html(self.widget, 'is_cool', None, html='<input type="checkbox" name="is_cool">')

    def test_render_false(self):
        self.check_html(self.widget, 'is_cool', False, html='<input type="checkbox" name="is_cool">')

    def test_render_true(self):
        """
        Tests the rendering of a checkbox widget with the `is_cool` field set to `True`. The function checks if the rendered HTML matches the expected output, which includes a checkbox input element with the `checked` attribute and the specified `name` attribute.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the rendered HTML does not match the expected output.
        
        Important Functions:
        - `check_html`: Compares the rendered HTML with the expected output
        """

        self.check_html(
            self.widget, 'is_cool', True,
            html='<input checked type="checkbox" name="is_cool">'
        )

    def test_render_value(self):
        """
        Using any value that's not in ('', None, False, True) will check the
        checkbox and set the 'value' attribute.
        """
        self.check_html(
            self.widget, 'is_cool', 'foo',
            html='<input checked type="checkbox" name="is_cool" value="foo">',
        )

    def test_render_int(self):
        """
        Integers are handled by value, not as booleans (#17114).
        """
        self.check_html(
            self.widget, 'is_cool', 0,
            html='<input checked type="checkbox" name="is_cool" value="0">',
        )
        self.check_html(
            self.widget, 'is_cool', 1,
            html='<input checked type="checkbox" name="is_cool" value="1">',
        )

    def test_render_check_test(self):
        """
        You can pass 'check_test' to the constructor. This is a callable that
        takes the value and returns True if the box should be checked.
        """
        widget = CheckboxInput(check_test=lambda value: value.startswith('hello'))
        self.check_html(widget, 'greeting', '', html=(
            '<input type="checkbox" name="greeting">'
        ))
        self.check_html(widget, 'greeting', 'hello', html=(
            '<input checked type="checkbox" name="greeting" value="hello">'
        ))
        self.check_html(widget, 'greeting', 'hello there', html=(
            '<input checked type="checkbox" name="greeting" value="hello there">'
        ))
        self.check_html(widget, 'greeting', 'hello & goodbye', html=(
            '<input checked type="checkbox" name="greeting" value="hello &amp; goodbye">'
        ))

    def test_render_check_exception(self):
        """
        Calling check_test() shouldn't swallow exceptions (#17888).
        """
        widget = CheckboxInput(
            check_test=lambda value: value.startswith('hello'),
        )

        with self.assertRaises(AttributeError):
            widget.render('greeting', True)

    def test_value_from_datadict(self):
        """
        The CheckboxInput widget will return False if the key is not found in
        the data dictionary (because HTML form submission doesn't send any
        result for unchecked checkboxes).
        """
        self.assertFalse(self.widget.value_from_datadict({}, {}, 'testing'))

    def test_value_from_datadict_string_int(self):
        value = self.widget.value_from_datadict({'testing': '0'}, {}, 'testing')
        self.assertIs(value, True)

    def test_value_omitted_from_data(self):
        self.assertIs(self.widget.value_omitted_from_data({'field': 'value'}, {}, 'field'), False)
        self.assertIs(self.widget.value_omitted_from_data({}, {}, 'field'), False)

    def test_get_context_does_not_mutate_attrs(self):
        """
        Tests that the `get_context` method of the widget does not mutate the input `attrs` dictionary.
        
        Args:
        self: The instance of the test case class.
        
        Attributes:
        attrs (dict): A dictionary containing the initial attributes, including 'checked' set to False.
        
        Methods:
        widget.get_context(name, value, attrs): Retrieves the context for the given widget attribute.
        
        Summary:
        This test ensures that calling `get_context` with `attrs` does not alter
        """

        attrs = {'checked': False}
        self.widget.get_context('name', True, attrs)
        self.assertIs(attrs['checked'], False)
