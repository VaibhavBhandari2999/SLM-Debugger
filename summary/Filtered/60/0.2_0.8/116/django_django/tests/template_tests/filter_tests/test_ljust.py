from django.template.defaultfilters import ljust
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class LjustTests(SimpleTestCase):
    @setup(
        {
            "ljust01": (
                '{% autoescape off %}.{{ a|ljust:"5" }}. .{{ b|ljust:"5" }}.'
                "{% endautoescape %}"
            )
        }
    )
    def test_ljust01(self):
        """
        Tests the ljust filter in a template context.
        The function takes a Django template engine instance and renders a template named 'ljust01' with two context variables: 'a' and 'b'. Variable 'a' is a regular string containing 'a&b', while 'b' is a marked safe string also containing 'a&b'. The expected output is a string with specific formatting: ".a&b  . .a&b  ." where 'a&b' is
        """

        output = self.engine.render_to_string(
            "ljust01", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, ".a&b  . .a&b  .")

    @setup({"ljust02": '.{{ a|ljust:"5" }}. .{{ b|ljust:"5" }}.'})
    def test_ljust02(self):
        output = self.engine.render_to_string(
            "ljust02", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, ".a&amp;b  . .a&b  .")


class FunctionTests(SimpleTestCase):
    def test_ljust(self):
        self.assertEqual(ljust("test", 10), "test      ")
        self.assertEqual(ljust("test", 3), "test")

    def test_less_than_string_length(self):
        self.assertEqual(ljust("test", 3), "test")

    def test_non_string_input(self):
        self.assertEqual(ljust(123, 4), "123 ")
4), "123 ")
