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
        Test rendering template with `addslashes` filter applied to variables.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the rendering of a template using the `render_to_string` method from an engine object. It applies the `addslashes` filter to the variables 'a' and 'b', which are passed as context data. The expected output is compared against the actual output to ensure correctness.
        
        Variables:
        - a (str): A string containing
        """

        output = self.engine.render_to_string(
            "addslashes01", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"<a>\' <a>\'")

    @setup({"addslashes02": "{{ a|addslashes }} {{ b|addslashes }}"})
    def test_addslashes02(self):
        """
        Test rendering template with `addslashes` filter applied to variables.
        
        This test checks that the `addslashes` filter correctly escapes special characters
        in the input variables 'a' and 'b'. The `mark_safe` function is used to ensure that
        'b' is not escaped, while 'a' is escaped using the `addslashes` filter.
        
        Args:
        None
        
        Returns:
        None
        
        Variables:
        output (str): The rendered template
        """

        output = self.engine.render_to_string(
            "addslashes02", {"a": "<a>'", "b": mark_safe("<a>'")}
        )
        self.assertEqual(output, r"&lt;a&gt;\&#x27; <a>\'")


class FunctionTests(SimpleTestCase):
    def test_quotes(self):
        """
        Test the `addslashes` function with input containing both double and single quotes, ensuring that the function correctly escapes the quotes by using backslashes before them.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `addslashes`: The function being tested, which is expected to escape double and single quotes in the input string.
        
        Input:
        - `"double quotes" and 'single quotes'`
        
        Output:
        - `\\\"double quotes\\\" and
        """

        self.assertEqual(
            addslashes("\"double quotes\" and 'single quotes'"),
            "\\\"double quotes\\\" and \\'single quotes\\'",
        )

    def test_backslashes(self):
        self.assertEqual(addslashes(r"\ : backslashes, too"), "\\\\ : backslashes, too")

    def test_non_string_input(self):
        self.assertEqual(addslashes(123), "123")
