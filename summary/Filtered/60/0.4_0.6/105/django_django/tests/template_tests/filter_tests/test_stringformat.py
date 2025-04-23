from django.template.defaultfilters import stringformat
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class StringformatTests(SimpleTestCase):
    """
    Notice that escaping is applied *after* any filters, so the string
    formatting here only needs to deal with pre-escaped characters.
    """

    @setup(
        {
            "stringformat01": (
                '{% autoescape off %}.{{ a|stringformat:"5s" }}. .'
                '{{ b|stringformat:"5s" }}.{% endautoescape %}'
            )
        }
    )
    def test_stringformat01(self):
        output = self.engine.render_to_string(
            "stringformat01", {"a": "a<b", "b": mark_safe("a<b")}
        )
        self.assertEqual(output, ".  a<b. .  a<b.")

    @setup(
        {"stringformat02": '.{{ a|stringformat:"5s" }}. .{{ b|stringformat:"5s" }}.'}
    )
    def test_stringformat02(self):
        output = self.engine.render_to_string(
            "stringformat02", {"a": "a<b", "b": mark_safe("a<b")}
        )
        self.assertEqual(output, ".  a&lt;b. .  a<b.")


class FunctionTests(SimpleTestCase):
    def test_format(self):
        """
        Tests the stringformat function.
        
        Args:
        value (int, list, tuple, set, dict): The value to be formatted.
        format_spec (str): The format specification to be applied.
        
        Returns:
        str: The formatted string representation of the input value.
        
        Test cases:
        - stringformat(1, "03d") should return "001".
        - stringformat([1, None], "s") should return "[1, None]".
        - stringformat
        """

        self.assertEqual(stringformat(1, "03d"), "001")
        self.assertEqual(stringformat([1, None], "s"), "[1, None]")
        self.assertEqual(stringformat((1, 2, 3), "s"), "(1, 2, 3)")
        self.assertEqual(stringformat((1,), "s"), "(1,)")
        self.assertEqual(stringformat({1, 2}, "s"), "{1, 2}")
        self.assertEqual(stringformat({1: 2, 2: 3}, "s"), "{1: 2, 2: 3}")

    def test_invalid(self):
        self.assertEqual(stringformat(1, "z"), "")
        self.assertEqual(stringformat(object(), "d"), "")
        self.assertEqual(stringformat(None, "d"), "")
        self.assertEqual(stringformat((1, 2, 3), "d"), "")
