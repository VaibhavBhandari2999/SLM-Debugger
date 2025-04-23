from django.template.defaultfilters import lower
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class LowerTests(SimpleTestCase):
    @setup(
        {
            "lower01": (
                "{% autoescape off %}{{ a|lower }} {{ b|lower }}{% endautoescape %}"
            )
        }
    )
    def test_lower01(self):
        """
        Tests the rendering of lowercasing functionality in a template engine.
        This function tests the rendering of lowercasing on strings and safely marked strings. It takes a template context with two variables: 'a' and 'b'. Variable 'a' is a regular string containing special characters, while 'b' is a safely marked string with special characters. The function renders the template 'lower01' with the provided context and checks if the output matches the expected result, which is the lowercase version of
        """

        output = self.engine.render_to_string(
            "lower01", {"a": "Apple & banana", "b": mark_safe("Apple &amp; banana")}
        )
        self.assertEqual(output, "apple & banana apple &amp; banana")

    @setup({"lower02": "{{ a|lower }} {{ b|lower }}"})
    def test_lower02(self):
        """
        Tests the rendering of a template with two variables: 'a' and 'b'. Both variables contain strings with special characters. The function uses the `render_to_string` method from an engine to render the template. Variable 'a' is a regular string, while 'b' is a marked safe string using `mark_safe`. The expected output is a string where both variables are converted to lowercase, with 'b' retaining its HTML escaping.
        
        Parameters:
        - self: The test case instance.
        
        Returns
        """

        output = self.engine.render_to_string(
            "lower02", {"a": "Apple & banana", "b": mark_safe("Apple &amp; banana")}
        )
        self.assertEqual(output, "apple &amp; banana apple &amp; banana")


class FunctionTests(SimpleTestCase):
    def test_lower(self):
        self.assertEqual(lower("TEST"), "test")

    def test_unicode(self):
        # uppercase E umlaut
        self.assertEqual(lower("\xcb"), "\xeb")

    def test_non_string_input(self):
        self.assertEqual(lower(123), "123")
