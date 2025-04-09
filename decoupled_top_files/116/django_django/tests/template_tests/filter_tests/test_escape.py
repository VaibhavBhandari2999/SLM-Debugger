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
        Tests the rendering of escaped and marked safe strings using the engine's render_to_string method. The input variables 'a' and 'b' are passed as context data, with 'a' being an unmarked string and 'b' being a marked safe string. The expected output is a string where 'a' is escaped and 'b' is not escaped.
        
        Args:
        self: The test case instance.
        
        Returns:
        None
        
        Methods Used:
        - `render_to_string
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
        """
        Tests the rendering of escaped and marked safe strings using the engine's render_to_string method. The input variables 'a' and 'b' are passed as context data, with 'a' being an unmarked string and 'b' being a marked safe string. The expected output is a string where 'a' is escaped and 'b' is not escaped.
        
        Args:
        self: The test case instance.
        
        Returns:
        None
        
        Methods Used:
        - `render_to_string
        """

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
        Tests the escaping of a lazy string using the `escape` function.
        
        This test case checks if the `escape` function correctly processes a lazy string created by the `lazy` function. The `lazy` function is used to create a string that will be concatenated with "special characters > here". The resulting string is then passed to the `escape` function to ensure proper HTML escaping. The test verifies that the output is an instance of `Promise` and contains the expected escaped HTML content.
        """

        add_html = lazy(lambda string: string + "special characters > here", str)
        escaped = escape(add_html("<some html & "))
        self.assertIsInstance(escaped, Promise)
        self.assertEqual(escaped, "&lt;some html &amp; special characters &gt; here")


class FunctionTests(SimpleTestCase):
    def test_non_string_input(self):
        self.assertEqual(escape(123), "123")
