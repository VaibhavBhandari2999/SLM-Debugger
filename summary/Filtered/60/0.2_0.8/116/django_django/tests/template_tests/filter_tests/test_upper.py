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
        output = self.engine.render_to_string(
            "upper01", {"a": "a & b", "b": mark_safe("a &amp; b")}
        )
        self.assertEqual(output, "A & B A &AMP; B")

    @setup({"upper02": "{{ a|upper }} {{ b|upper }}"})
    def test_upper02(self):
        """
        Tests the rendering of upper-cased strings with special characters. The function takes a Django template engine instance (`self.engine`) and renders a template named 'upper02' with two context variables: 'a' and 'b'. Variable 'a' contains the string 'a & b', and 'b' contains the string 'a &amp; b' marked as safe. The expected output is 'A &amp; B A &AMP; B', where 'A &amp; B'
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
        self.assertEqual(upper(123), "123")
