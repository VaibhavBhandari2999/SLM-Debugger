from django.template.defaultfilters import upper
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class UpperTests(SimpleTestCase):
    """
    The "upper" filter messes up entities (which are case-sensitive),
    so it's not safe for non-escaping purposes.
    """

    @setup(
        {
            "upper01": (
                "{% autoescape off %}{{ a|upper }} {{ b|upper }}{% endautoescape %}"
            )
        }
    )
    def test_upper01(self):
        """
        Tests the rendering of upper-cased strings and safe HTML entities.
        
        This function tests the `render_to_string` method of the `engine` object by passing it a template named "upper01" and a context dictionary containing two variables: 'a' and 'b'. The variable 'a' is a simple string, while 'b' is a safe HTML entity. The expected output is a string where 'a' is upper-cased and 'b' retains its HTML entity form.
        
        Parameters
        """

        output = self.engine.render_to_string(
            "upper01", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "A & B A &AMP; B")

    @setup({"upper02": "{{ a|upper }} {{ b|upper }}"})
    def test_upper02(self):
        """
        Tests the rendering of upper-cased strings with special characters.
        
        This function tests the `render_to_string` method of the `engine` object by passing a template named 'upper02' and a context containing two variables: 'a' and 'b'. The variable 'a' is a string with special characters, and 'b' is a string with special characters that have been marked as safe to prevent HTML escaping. The expected output is a string where both 'a' and 'b'
        """

        output = self.engine.render_to_string(
            "upper02", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "A &amp; B A &amp;AMP; B")


class FunctionTests(SimpleTestCase):
    def test_upper(self):
        self.assertEqual(upper("Mixed case input"), "MIXED CASE INPUT")

    def test_unicode(self):
        # lowercase e umlaut
        self.assertEqual(upper("\xeb"), "\xcb")

    def test_non_string_input(self):
        self.assertEqual(upper(123), "123")
