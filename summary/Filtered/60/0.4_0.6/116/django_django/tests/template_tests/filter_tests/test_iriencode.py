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
        output = self.engine.render_to_string(
            "iriencode03", {"url": mark_safe("?test=1&me=2")}
        )
        self.assertEqual(output, "?test=1&me=2")

    @setup(
        {"iriencode04": "{% autoescape off %}{{ url|iriencode }}{% endautoescape %}"}
    )
    def test_iriencode04(self):
        """
        Tests the `iriencode04` template filter.
        
        This function renders a template with a URL that has already been marked as safe. The expected output is the same as the input, as the URL is already safe to be included in an IRI (Internationalized Resource Identifier).
        
        Parameters:
        - `self`: The test case instance.
        
        Returns:
        - `None`: The function asserts the expected output and does not return any value.
        
        Key Parameters:
        - `url`: A string representing a URL that has
        """

        output = self.engine.render_to_string(
            "iriencode04", {"url": mark_safe("?test=1&me=2")}
        )
        self.assertEqual(output, "?test=1&me=2")


class FunctionTests(SimpleTestCase):
    def test_unicode(self):
        self.assertEqual(iriencode("S\xf8r-Tr\xf8ndelag"), "S%C3%B8r-Tr%C3%B8ndelag")

    def test_urlencoded(self):
        self.assertEqual(
            iriencode(urlencode("fran\xe7ois & jill")), "fran%C3%A7ois%20%26%20jill"
        )
