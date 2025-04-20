from django.template.defaultfilters import escape
from django.test import SimpleTestCase
from django.utils.functional import Promise, lazy
from django.utils.safestring import mark_safe

from ..utils import setup


class EscapeTests(SimpleTestCase):
    """
    The "escape" filter works the same whether autoescape is on or off,
    but it has no effect on strings already marked as safe.
    """

    @setup({"escape01": "{{ a|escape }} {{ b|escape }}"})
    def test_escape01(self):
        """
        Tests the rendering of escaped and unescaped strings.
        
        This function tests the rendering of two variables, 'a' and 'b', using the `render_to_string` method of `engine`. Variable 'a' contains the string "x&y" which is expected to be escaped, while 'b' contains the same string but wrapped in `mark_safe` to prevent escaping. The expected output is "x&amp;y x&y".
        
        Parameters:
        self: The current test case instance.
        
        Returns
        """

        output = self.engine.render_to_string(
            "escape01", {"a": "x&y", "b": mark_safe("x&y")}
        )
        self.assertEqual(output, "x&amp;y x&y")

    @setup(
        {
            "escape02": (
                "{% autoescape off %}{{ a|escape }} {{ b|escape }}{% endautoescape %}"
            )
        }
    )
    def test_escape02(self):
        output = self.engine.render_to_string(
            "escape02", {"a": "x&y", "b": mark_safe("x&y")}
        )
        self.assertEqual(output, "x&amp;y x&y")

    @setup({"escape03": "{% autoescape off %}{{ a|escape|escape }}{% endautoescape %}"})
    def test_escape03(self):
        output = self.engine.render_to_string("escape03", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    @setup({"escape04": "{{ a|escape|escape }}"})
    def test_escape04(self):
        output = self.engine.render_to_string("escape04", {"a": "x&y"})
        self.assertEqual(output, "x&amp;y")

    def test_escape_lazy_string(self):
        """
        Tests the escape function with a lazy string.
        
        This test checks if the escape function correctly processes a lazy string that appends "special characters > here" to the input string. The input string is "<some html & ".
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The type of the result should be a Promise.
        - The result should be equal to "&lt;some html &amp; special characters &gt; here".
        """

        add_html = lazy(lambda string: string + "special characters > here", str)
        escaped = escape(add_html("<some html & "))
        self.assertIsInstance(escaped, Promise)
        self.assertEqual(escaped, "&lt;some html &amp; special characters &gt; here")


class FunctionTests(SimpleTestCase):
    def test_non_string_input(self):
        self.assertEqual(escape(123), "123")
