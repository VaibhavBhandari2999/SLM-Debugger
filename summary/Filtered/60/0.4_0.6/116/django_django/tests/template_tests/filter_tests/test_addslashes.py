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
        """
        Test the behavior of the `addslashes` function on template variables.
        
        This test checks how the `addslashes` function processes both regular string and `mark_safe`-marked string variables. The function should escape special characters in the strings for safe output in templates.
        
        Parameters:
        - a (str): A regular string containing special characters.
        - b (SafeString): A string marked as safe, containing special characters.
        
        Returns:
        str: The rendered output with escaped special characters.
        """

        output = self.engine.render_to_string(
            "addslashes01", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"<a>\' <a>\'")

    @setup({"addslashes02": "{{ a|addslashes }} {{ b|addslashes }}"})
    def test_addslashes02(self):
        """
        Tests the behavior of the `addslashes` function on a template string.
        
        This function renders a template with two variables, `a` and `b`. Variable `a` is a string containing an HTML entity, while `b` is a `mark_safe`-wrapped version of the same string. The expected output is a string where the slashes in both variables are added, but the `mark_safe`-wrapped variable should not be further escaped.
        
        Parameters:
        None
        
        Returns:
        None
        """

        output = self.engine.render_to_string(
            "addslashes02", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"&lt;a&gt;\&#x27; <a>\'")


class FunctionTests(SimpleTestCase):
    def test_quotes(self):
        self.assertEqual(
            addslashes("\"double quotes\" and 'single quotes'"),
            "\\\"double quotes\\\" and \\'single quotes\\'",
        )

    def test_backslashes(self):
        self.assertEqual(addslashes(r"\ : backslashes, too"), "\\\\ : backslashes, too")

    def test_non_string_input(self):
        self.assertEqual(addslashes(123), "123")
