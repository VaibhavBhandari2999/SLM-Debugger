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
        output = self.engine.render_to_string(
            "cut01", {"a": "x&y", "b": mark_safe("x&amp;y")}
        )
        self.assertEqual(output, "&y &amp;y")

    @setup({"cut02": '{{ a|cut:"x" }} {{ b|cut:"x" }}'})
    def test_cut02(self):
        """
        Tests the rendering of template strings with special characters and safe strings.
        
        This function tests the rendering of template strings that contain special characters and safe strings. It takes a Django template engine instance (`self.engine`), a template name (`"cut02"`), and a context dictionary with two keys: 'a' and 'b'. The value of 'a' is a string containing an ampersand, and the value of 'b' is a safe string containing an ampersand. The function
        """

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
        Tests the rendering of template strings with both plain text and marked safe HTML content.
        
        This function evaluates the output of a template rendering engine for a specific template ("cut06") with two variables:
        - 'a': A plain text string containing ampersands and other special characters.
        - 'b': A marked safe HTML string containing ampersands and other special characters.
        
        The expected output is "x&amp;y x&amp;ampy", where the ampersands in 'b' are properly escaped to
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
        """
        Test the function to check if a non-matching string is correctly handled.
        
        Args:
        input_string (str): The string to be checked.
        pattern (str): The pattern to be matched.
        
        Returns:
        str: The original input string if it does not match the pattern.
        """

        self.assertEqual(
            cut("a string to be mangled", "strings"), "a string to be mangled"
        )

    def test_non_string_input(self):
        self.assertEqual(cut(123, "2"), "13")
