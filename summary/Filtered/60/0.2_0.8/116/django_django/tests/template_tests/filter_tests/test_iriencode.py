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
        Tests the rendering of a template with an encoded URL parameter.
        
        This function tests the `render_to_string` method of a template engine with a context containing a URL that has already been marked as safe. The expected output is the same as the input, as the URL is not further encoded.
        
        Parameters:
        - `self`: The instance of the test case class.
        
        Returns:
        - None: This function asserts the expected output but does not return any value.
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
        Tests the encoding of a URL with special characters.
        
        This function encodes a given URL string that contains special characters, ensuring that the encoded output matches the expected format. The input is a URL string with a French name containing accented characters and a space, along with an ampersand. The expected output is the URL-encoded version of the input string, where special characters are replaced with their percent-encoded equivalents.
        
        Parameters:
        - url (str): The URL string to be encoded, containing special characters
        """

        self.assertEqual(
            iriencode(urlencode("fran\xe7ois & jill")), "fran%C3%A7ois%20%26%20jill"
        )
