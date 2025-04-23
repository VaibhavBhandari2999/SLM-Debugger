from django.template.defaultfilters import escapejs_filter
from django.test import SimpleTestCase
from django.utils.functional import lazy

from ..utils import setup


class EscapejsTests(SimpleTestCase):
    @setup({"escapejs01": "{{ a|escapejs }}"})
    def test_escapejs01(self):
        output = self.engine.render_to_string(
            "escapejs01", {"a": "testing\r\njavascript 'string\" <b>escaping</b>"}
        )
        self.assertEqual(
            output,
            "testing\\u000D\\u000Ajavascript "
            "\\u0027string\\u0022 \\u003Cb\\u003E"
            "escaping\\u003C/b\\u003E",
        )

    @setup({"escapejs02": "{% autoescape off %}{{ a|escapejs }}{% endautoescape %}"})
    def test_escapejs02(self):
        """
        Tests the escapejs functionality for a template string with special characters.
        
        This function renders a template string using the provided engine and checks if the output correctly escapes the special characters in the input string. The input string contains newline, single quote, double quote, and HTML tag characters. The function expects the rendered output to match a specific expected string that represents the escaped characters.
        
        Parameters:
        self: The test case instance (unittest.TestCase).
        
        Returns:
        None: The function asserts the expected output and does not
        """

        output = self.engine.render_to_string(
            "escapejs02", {"a": "testing\r\njavascript 'string\" <b>escaping</b>"}
        )
        self.assertEqual(
            output,
            "testing\\u000D\\u000Ajavascript "
            "\\u0027string\\u0022 \\u003Cb\\u003E"
            "escaping\\u003C/b\\u003E",
        )


class FunctionTests(SimpleTestCase):
    def test_quotes(self):
        self.assertEqual(
            escapejs_filter("\"double quotes\" and 'single quotes'"),
            "\\u0022double quotes\\u0022 and \\u0027single quotes\\u0027",
        )

    def test_backslashes(self):
        self.assertEqual(
            escapejs_filter(r"\ : backslashes, too"), "\\u005C : backslashes, too"
        )

    def test_whitespace(self):
        self.assertEqual(
            escapejs_filter("and lots of whitespace: \r\n\t\v\f\b"),
            "and lots of whitespace: \\u000D\\u000A\\u0009\\u000B\\u000C\\u0008",
        )

    def test_script(self):
        """
        Tests the escapejs_filter function with a script tag input.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the output of escapejs_filter does not match the expected result.
        
        Key Parameters:
        - `escapejs_filter`: The function to be tested, which takes a string input and returns a string with special characters escaped for use in JavaScript.
        - Input: The string "<script>and this</script>".
        - Expected Output: The string "\\u0
        """

        self.assertEqual(
            escapejs_filter(r"<script>and this</script>"),
            "\\u003Cscript\\u003Eand this\\u003C/script\\u003E",
        )

    def test_paragraph_separator(self):
        self.assertEqual(
            escapejs_filter("paragraph separator:\u2029and line separator:\u2028"),
            "paragraph separator:\\u2029and line separator:\\u2028",
        )

    def test_lazy_string(self):
        append_script = lazy(lambda string: r"<script>this</script>" + string, str)
        self.assertEqual(
            escapejs_filter(append_script("whitespace: \r\n\t\v\f\b")),
            "\\u003Cscript\\u003Ethis\\u003C/script\\u003E"
            "whitespace: \\u000D\\u000A\\u0009\\u000B\\u000C\\u0008",
        )
 
    """

        append_script = lazy(lambda string: r"<script>this</script>" + string, str)
        self.assertEqual(
            escapejs_filter(append_script("whitespace: \r\n\t\v\f\b")),
            "\\u003Cscript\\u003Ethis\\u003C/script\\u003E"
            "whitespace: \\u000D\\u000A\\u0009\\u000B\\u000C\\u0008",
        )
