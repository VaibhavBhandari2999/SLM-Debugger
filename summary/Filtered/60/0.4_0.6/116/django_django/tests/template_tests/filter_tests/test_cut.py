from django.template.defaultfilters import cut
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class CutTests(SimpleTestCase):
    @setup(
        {
            "cut01": (
                '{% autoescape off %}{{ a|cut:"x" }} {{ b|cut:"x" }}{% endautoescape %}'
            )
        }
    )
    def test_cut01(self):
        """
        Tests the rendering of template strings with special characters and SafeString objects.
        
        This function tests the behavior of the `render_to_string` method from the `engine` object when provided with a template string and a context containing both a regular string and a SafeString. The template string `cut01` is expected to strip leading and trailing characters, and the function checks if the output matches the expected result.
        
        Parameters:
        - `self`: The test case instance (from a unittest.TestCase subclass).
        
        Inputs:
        """

        output = self.engine.render_to_string(
            "cut01", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "&y &amp;y")

    @setup({"cut02": '{{ a|cut:"x" }} {{ b|cut:"x" }}'})
    def test_cut02(self):
        output = self.engine.render_to_string(
            "cut02", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "&amp;y &amp;y")

    @setup(
        {
            "cut03": (
                '{% autoescape off %}{{ a|cut:"&" }} {{ b|cut:"&" }}{% endautoescape %}'
            )
        }
    )
    def test_cut03(self):
        """
        Tests the behavior of the `render_to_string` method with special characters and `mark_safe` usage.
        
        This test checks how the `render_to_string` method processes a template with special characters and a marked-safe string. The method is expected to handle the special characters correctly and preserve the marked-safe string as is.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function asserts the expected output and does not return any value.
        
        Key Parameters:
        - `template_name`
        """

        output = self.engine.render_to_string(
            "cut03", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "xy xamp;y")

    @setup({"cut04": '{{ a|cut:"&" }} {{ b|cut:"&" }}'})
    def test_cut04(self):
        output = self.engine.render_to_string(
            "cut04", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "xy xamp;y")

    # Passing ';' to cut can break existing HTML entities, so those strings
    # are auto-escaped.
    @setup(
        {
            "cut05": (
                '{% autoescape off %}{{ a|cut:";" }} {{ b|cut:";" }}{% endautoescape %}'
            )
        }
    )
    def test_cut05(self):
        output = self.engine.render_to_string(
            "cut05", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "x&y x&ampy")

    @setup({"cut06": '{{ a|cut:";" }} {{ b|cut:";" }}'})
    def test_cut06(self):
        output = self.engine.render_to_string(
            "cut06", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "x&amp;y x&amp;ampy")


class FunctionTests(SimpleTestCase):
    def test_character(self):
        self.assertEqual(cut("a string to be mangled", "a"), " string to be mngled")

    def test_characters(self):
        self.assertEqual(cut("a string to be mangled", "ng"), "a stri to be maled")

    def test_non_matching_string(self):
        """
        Test the function to check if a non-matching string is correctly handled.
        
        Args:
        text (str): The string to be checked.
        pattern (str): The pattern to match against the string.
        
        Returns:
        str: The original string if it does not match the pattern.
        
        Raises:
        None
        
        Example:
        >>> cut("a string to be mangled", "strings")
        'a string to be mangled'
        """

        self.assertEqual(
            cut("a string to be mangled", "strings"), "a string to be mangled"
        )

    def test_non_string_input(self):
        self.assertEqual(cut(123, "2"), "13")
