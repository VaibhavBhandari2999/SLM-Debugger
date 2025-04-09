from django.template.defaultfilters import escapejs_filter
from django.test import SimpleTestCase
from django.utils.functional import lazy

from ..utils import setup


class EscapejsTests(SimpleTestCase):
    @setup({"escapejs01": "{{ a|escapejs }}"})
    def test_escapejs01(self):
        """
        Tests rendering of JavaScript strings with special characters using the escapejs template filter.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the rendering of a JavaScript string containing special characters such as newline, single quote, double quote, and HTML tags. The `render_to_string` method is used to render the template "escapejs01" with the given context. The expected output is compared against the actual output using the `assertEqual` method.
        
        Important
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
        """
        Tests rendering of JavaScript strings with special characters using the escapejs template filter.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the rendering of a JavaScript string containing special characters such as newline, single quote, double quote, and HTML tags. The `render_to_string` method is used to render the template "escapejs02" with the given context. The expected output is compared against the actual output using the `assertEqual` method.
        
        Important
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
        """
        Escapes double and single quotes in a string using JavaScript's escape mechanism, returning the escaped string.
        
        Args:
        value (str): The input string containing double and single quotes.
        
        Returns:
        str: The escaped string with double and single quotes represented as Unicode escape sequences.
        """

        self.assertEqual(
            escapejs_filter("\"double quotes\" and 'single quotes'"),
            "\\u0022double quotes\\u0022 and \\u0027single quotes\\u0027",
        )

    def test_backslashes(self):
        """
        Tests the `escapejs_filter` function with an input string containing backslashes. The function should escape backslashes using Unicode representation.
        
        Args:
        None (the test is run internally)
        
        Returns:
        None (the test asserts the expected output)
        
        Example:
        >>> escapejs_filter(r"\ : backslashes, too")
        '\\u005C : backslashes, too'
        """

        self.assertEqual(
            escapejs_filter(r"\ : backslashes, too"), "\\u005C : backslashes, too"
        )

    def test_whitespace(self):
        """
        Escapes whitespace characters in the input string and converts them to their corresponding Unicode escape sequences.
        
        Args:
        value (str): The input string containing whitespace characters.
        
        Returns:
        str: The escaped string with whitespace converted to Unicode escape sequences.
        """

        self.assertEqual(
            escapejs_filter("and lots of whitespace: \r\n\t\v\f\b"),
            "and lots of whitespace: \\u000D\\u000A\\u0009\\u000B\\u000C\\u0008",
        )

    def test_script(self):
        """
        Test the `escapejs_filter` function.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function tests the `escapejs_filter` function, which escapes
        special characters in a given string for use in JavaScript. The
        input is a string containing a script tag, and the expected output
        is the escaped version of the input string.
        """

        self.assertEqual(
            escapejs_filter(r"<script>and this</script>"),
            "\\u003Cscript\\u003Eand this\\u003C/script\\u003E",
        )

    def test_paragraph_separator(self):
        """
        Tests the `escapejs_filter` function for correctly handling paragraph separators (U+2029) and line separators (U+2028). The function should convert these Unicode characters into their escaped string representations.
        
        Args:
        None
        
        Returns:
        None
        
        Example:
        >>> test_paragraph_separator()
        assert escapejs_filter("paragraph separator:\u2029and line separator:\u2028") == "paragraph separator:\\u2029
        """

        self.assertEqual(
            escapejs_filter("paragraph separator:\u2029and line separator:\u2028"),
            "paragraph separator:\\u2029and line separator:\\u2028",
        )

    def test_lazy_string(self):
        """
        Test the behavior of the `escapejs_filter` function when applied to a `lazy` string that appends a script tag to its input. The `lazy` string is created using a lambda function that concatenates a predefined script tag with the input string. The `escapejs_filter` function is then used to escape the resulting string, ensuring that special characters are properly encoded for JavaScript. The test checks that the whitespace characters within the input string are correctly preserved and escaped in the output.
        """

        append_script = lazy(lambda string: r"<script>this</script>" + string, str)
        self.assertEqual(
            escapejs_filter(append_script("whitespace: \r\n\t\v\f\b")),
            "\\u003Cscript\\u003Ethis\\u003C/script\\u003E"
            "whitespace: \\u000D\\u000A\\u0009\\u000B\\u000C\\u0008",
        )
