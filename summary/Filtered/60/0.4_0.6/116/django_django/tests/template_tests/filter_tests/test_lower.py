from django.template.defaultfilters import lower
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class LowerTests(SimpleTestCase):
    @setup(
        {
            "lower01": (
                "{% autoescape off %}{{ a|lower }} {{ b|lower }}{% endautoescape %}"
            )
        }
    )
    def test_lower01(self):
        """
        Tests the rendering of lowercasing functionality in a template engine.
        
        This function tests the rendering of lowercase conversion in a template engine. It takes a context dictionary with two keys: 'a' and 'b'. The value of 'a' is a string with special characters, and the value of 'b' is a string with special characters that has been marked as safe. The function renders the template 'lower01' with this context and checks if the output matches the expected result, which is
        """

        output = self.engine.render_to_string(
            "lower01", {"a": "Apple & banana", "b": mark_safe("Apple &amp; banana")}
        )
        self.assertEqual(output, "apple & banana apple &amp; banana")

    @setup({"lower02": "{{ a|lower }} {{ b|lower }}"})
    def test_lower02(self):
        """
        Tests the rendering of lower-cased strings with and without mark_safe.
        
        This function tests the rendering of lower-cased strings using the engine's render_to_string method. It takes a template named 'lower02' and a context dictionary containing two keys: 'a' and 'b'. The value of 'a' is a string with special characters, and the value of 'b' is the same string but wrapped with mark_safe to prevent auto-escaping. The function then compares the rendered output
        """

        output = self.engine.render_to_string(
            "lower02", {"a": "Apple & banana", "b": mark_safe("Apple &amp; banana")}
        )
        self.assertEqual(output, "apple &amp; banana apple &amp; banana")


class FunctionTests(SimpleTestCase):
    def test_lower(self):
        self.assertEqual(lower("TEST"), "test")

    def test_unicode(self):
        # uppercase E umlaut
        self.assertEqual(lower("\xcb"), "\xeb")

    def test_non_string_input(self):
        self.assertEqual(lower(123), "123")
