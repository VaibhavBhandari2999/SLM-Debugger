from django.template.defaultfilters import escapejs_filter
from django.test import SimpleTestCase
from django.utils.functional import lazy

from ..utils import setup


class EscapejsTests(SimpleTestCase):
    @setup({"escapejs01": "{{ a|escapejs }}"})
    def test_escapejs01(self):
        """
        Test rendering a template with JavaScript escaping.
        
        This function tests the rendering of a template with a string containing
        special characters that need to be escaped in JavaScript. The template
        receives a dictionary with a single key 'a' whose value is a string
        containing newlines, single and double quotes, and HTML tags. The expected
        output is a string where these characters are properly escaped for JavaScript
        use.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> test_escapejs
        """

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
        """
        Test the escapejs_filter function with a string containing backslashes.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `r"\ : backslashes, too"`: The input string containing backslashes to be escaped.
        
        Expected Output:
        - `"\\u005C : backslashes, too"`: The escaped string where each backslash is replaced with its Unicode representation.
        """

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
        Tests the escapejs_filter function to ensure it correctly escapes HTML tags within a JavaScript script element. The function takes a string containing a JavaScript script element and returns its escaped version. The input is a raw string with a script element, and the output is a string with the script element's content and tags escaped using Unicode escape sequences.
        
        :param self: The instance of the class containing this method.
        :type self: object
        :param value: The raw string containing a script element to be escaped.
        :type value:
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
