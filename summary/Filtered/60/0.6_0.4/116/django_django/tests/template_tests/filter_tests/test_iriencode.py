from django.template.defaultfilters import iriencode, urlencode
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class IriencodeTests(SimpleTestCase):
    """
    Ensure iriencode keeps safe strings.
    """

    @setup({"iriencode01": "{{ url|iriencode }}"})
    def test_iriencode01(self):
        output = self.engine.render_to_string("iriencode01", {"url": "?test=1&me=2"})
        self.assertEqual(output, "?test=1&amp;me=2")

    @setup(
        {"iriencode02": "{% autoescape off %}{{ url|iriencode }}{% endautoescape %}"}
    )
    def test_iriencode02(self):
        output = self.engine.render_to_string("iriencode02", {"url": "?test=1&me=2"})
        self.assertEqual(output, "?test=1&me=2")

    @setup({"iriencode03": "{{ url|iriencode }}"})
    def test_iriencode03(self):
        """
        Tests the rendering of a template with an IRIsafe URL.
        
        This function tests the rendering of a template that contains a URL with query parameters. The URL is marked as safe to prevent it from being escaped during rendering. The expected output is the same as the input URL.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses `mark_safe` to mark the URL as safe for rendering.
        - The rendered output should match the input URL, which includes query parameters.
        """

        output = self.engine.render_to_string(
            "iriencode03", {"url": mark_safe("?test=1&me=2")}
        )
        self.assertEqual(output, "?test=1&me=2")

    @setup(
        {"iriencode04": "{% autoescape off %}{{ url|iriencode }}{% endautoescape %}"}
    )
    def test_iriencode04(self):
        output = self.engine.render_to_string(
            "iriencode04", {"url": mark_safe("?test=1&me=2")}
        )
        self.assertEqual(output, "?test=1&me=2")


class FunctionTests(SimpleTestCase):
    def test_unicode(self):
        self.assertEqual(iriencode("S\xf8r-Tr\xf8ndelag"), "S%C3%B8r-Tr%C3%B8ndelag")

    def test_urlencoded(self):
        """
        Tests the encoding of a URL query string with special characters.
        
        This function encodes a given string using URL encoding and then encodes the resulting string using IRI encoding. The test checks if the encoded string matches the expected output.
        
        Parameters:
        - value (str): The input string containing special characters to be URL-encoded.
        
        Returns:
        None: This function is used for testing and does not return any value. It asserts the correctness of the encoding process.
        
        Example:
        >>> test_urlencoded("
        """

        self.assertEqual(
            iriencode(urlencode("fran\xe7ois & jill")), "fran%C3%A7ois%20%26%20jill"
        )
