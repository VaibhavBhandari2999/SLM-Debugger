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
        Tests the `cut` template filter with different inputs.
        
        This function tests the `cut` template filter by rendering a template with two different input values:
        - `a`: A string containing an ampersand followed by 'y' (i.e., "x&y").
        - `b`: A string containing an HTML-escaped ampersand followed by 'y' (i.e., "x&amp;y"), wrapped in `mark_safe` to prevent auto-escaping.
        
        The `cut` filter
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
        output = self.engine.render_to_string(
            "cut03", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "xy xamp;y")

    @setup({"cut04": '{{ a|cut:"&" }} {{ b|cut:"&" }}'})
    def test_cut04(self):
        """
        Tests the rendering of template strings with special characters and SafeString objects.
        
        This function tests the rendering behavior of a template engine when dealing with strings containing HTML special characters and SafeString objects. It checks if the engine correctly handles these inputs and produces the expected output.
        
        Parameters:
        self: The test case instance.
        
        Returns:
        None: This function asserts the expected output and does not return any value.
        
        Key Parameters:
        - `a`: A regular string containing HTML special characters.
        - `b
        """

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
        """
        Tests the behavior of the `render_to_string` method with special characters and `mark_safe` usage.
        
        Parameters:
        - `self`: The test case instance (unittest.TestCase).
        
        Inputs:
        - Template name: "cut06"
        - Context data: A dictionary containing two key-value pairs:
        - "a": A string with special characters ("x&y").
        - "b": A string with special characters marked as safe using `mark_safe` ("x&amp;y").
        
        Outputs:
        - The
        """

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
        self.assertEqual(
            cut("a string to be mangled", "strings"), "a string to be mangled"
        )

    def test_non_string_input(self):
        self.assertEqual(cut(123, "2"), "13")
