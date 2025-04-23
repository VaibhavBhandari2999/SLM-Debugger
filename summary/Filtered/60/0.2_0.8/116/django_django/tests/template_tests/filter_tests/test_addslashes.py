from django.template.defaultfilters import addslashes
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class AddslashesTests(SimpleTestCase):
    @setup(
        {
            "addslashes01": (
                "{% autoescape off %}{{ a|addslashes }} {{ b|addslashes }}"
                "{% endautoescape %}"
            )
        }
    )
    def test_addslashes01(self):
        output = self.engine.render_to_string(
            "addslashes01", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"<a>\' <a>\'")

    @setup({"addslashes02": "{{ a|addslashes }} {{ b|addslashes }}"})
    def test_addslashes02(self):
        """
        Tests the behavior of the `addslashes` template filter on a string and a `mark_safe` string.
        
        Parameters:
        - `self`: The current test case instance.
        
        Returns:
        - None: This function asserts the expected output by comparing it with the actual output.
        
        Key Variables:
        - `a`: A string containing an HTML entity.
        - `b`: A `mark_safe` string containing an HTML entity.
        
        Expected Output:
        - The rendered string should escape the HTML entities and single quotes properly, resulting
        """

        output = self.engine.render_to_string(
            "addslashes02", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"&lt;a&gt;\&#x27; <a>\'")


class FunctionTests(SimpleTestCase):
    def test_quotes(self):
        """
        Test the `addslashes` function to ensure it correctly escapes double and single quotes in a string.
        
        Args:
        None (This is a test function and does not take any arguments).
        
        Returns:
        None (This function asserts the correctness of the `addslashes` function).
        
        Example:
        >>> test_quotes()
        This test case checks if the `addslashes` function properly escapes double quotes and single quotes in the input string "double quotes" and 'single quotes'. The expected output is a string
        """

        self.assertEqual(
            addslashes("\"double quotes\" and 'single quotes'"),
            "\\\"double quotes\\\" and \\'single quotes\\'",
        )

    def test_backslashes(self):
        self.assertEqual(addslashes(r"\ : backslashes, too"), "\\\\ : backslashes, too")

    def test_non_string_input(self):
        self.assertEqual(addslashes(123), "123")
