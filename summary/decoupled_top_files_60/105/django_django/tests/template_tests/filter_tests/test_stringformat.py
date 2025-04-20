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
        """
        Tests the rendering of strings with special characters using string formatting in a template engine.
        
        This function tests the rendering of strings containing special characters, both as plain strings and as marked safe HTML, to ensure they are correctly formatted and escaped in the output.
        
        Parameters:
        self: The test case object.
        
        Returns:
        None: This function asserts the expected output and does not return any value.
        
        Key Parameters:
        a (str): A plain string containing special characters ('a<b').
        b (SafeString
        """

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
        self.assertEqual(stringformat(1, "03d"), "001")
        self.assertEqual(stringformat([1, None], "s"), "[1, None]")
        self.assertEqual(stringformat((1, 2, 3), "s"), "(1, 2, 3)")
        self.assertEqual(stringformat((1,), "s"), "(1,)")
        self.assertEqual(stringformat({1, 2}, "s"), "{1, 2}")
        self.assertEqual(stringformat({1: 2, 2: 3}, "s"), "{1: 2, 2: 3}")

    def test_invalid(self):
        """
        Test the stringformat function with various invalid inputs.
        
        This test function checks the behavior of the stringformat function when given invalid or unsupported types as inputs. The function should return an empty string for the following cases:
        - When the first argument is an integer and the second argument is an unsupported format string.
        - When the first argument is an unsupported type (e.g., object).
        - When the first argument is None.
        - When the first argument is a tuple and the second argument is an unsupported format string
        """

        self.assertEqual(stringformat(1, "z"), "")
        self.assertEqual(stringformat(object(), "d"), "")
        self.assertEqual(stringformat(None, "d"), "")
        self.assertEqual(stringformat((1, 2, 3), "d"), "")
