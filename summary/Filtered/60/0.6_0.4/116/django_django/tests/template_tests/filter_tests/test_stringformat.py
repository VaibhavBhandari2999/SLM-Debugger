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
        value: The value to be formatted. Can be an integer, list, tuple, or dictionary.
        format_spec: A string specifying the format. Common options include '03d' for a 3-digit integer with leading zeros, 's' for a string representation of the value.
        
        Returns:
        A string representation of the input value according to the specified format.
        
        Examples:
        >>> stringformat(1, "03d")
        '
        """

        self.assertEqual(stringformat(1, "03d"), "001")
        self.assertEqual(stringformat([1, None], "s"), "[1, None]")
        self.assertEqual(stringformat((1, 2, 3), "s"), "(1, 2, 3)")
        self.assertEqual(stringformat((1,), "s"), "(1,)")
        self.assertEqual(stringformat({1, 2}, "s"), "{1, 2}")
        self.assertEqual(stringformat({1: 2, 2: 3}, "s"), "{1: 2, 2: 3}")

    def test_invalid(self):
        """
        Tests the stringformat function with various invalid inputs.
        
        This function tests the stringformat function with different types of invalid inputs to ensure it handles them correctly. The function does not return any value but uses assertEqual to check the expected output.
        
        Parameters:
        None (The function uses predefined test cases within the test_invalid method)
        
        Returns:
        None (The function uses assertEqual to validate the expected output)
        
        Key Parameters:
        - No parameters
        
        Key Keywords:
        - No keywords
        
        Input Details:
        """

        self.assertEqual(stringformat(1, "z"), "")
        self.assertEqual(stringformat(object(), "d"), "")
        self.assertEqual(stringformat(None, "d"), "")
        self.assertEqual(stringformat((1, 2, 3), "d"), "")
f.assertEqual(stringformat((1, 2, 3), "d"), "")
