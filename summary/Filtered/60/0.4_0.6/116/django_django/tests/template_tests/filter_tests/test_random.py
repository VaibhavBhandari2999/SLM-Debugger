from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class RandomTests(SimpleTestCase):
    @setup({"random01": "{{ a|random }} {{ b|random }}"})
    def test_random01(self):
        """
        Tests the rendering of a template with a string containing HTML entities.
        
        This function tests the rendering of a template named 'random01' with a context containing two lists. Each list contains strings with HTML entities. The `mark_safe` function is used to mark the strings as safe for rendering without escaping. The expected output is a string where the HTML entities are preserved.
        
        Parameters:
        self: The instance of the test case class.
        
        Returns:
        None: This function asserts the expected output and does
        """

        output = self.engine.render_to_string(
            "random01", {"a": ["a&b", "a&b"], "b": [mark_safe("a&b"), mark_safe("a&b")]}
        )
        self.assertEqual(output, "a&amp;b a&b")

    @setup(
        {
            "random02": (
                "{% autoescape off %}{{ a|random }} {{ b|random }}{% endautoescape %}"
            )
        }
    )
    def test_random02(self):
        output = self.engine.render_to_string(
            "random02", {"a": ["a&b", "a&b"], "b": [mark_safe("a&b"), mark_safe("a&b")]}
        )
        self.assertEqual(output, "a&b a&b")

    @setup({"empty_list": "{{ list|random }}"})
    def test_empty_list(self):
        output = self.engine.render_to_string("empty_list", {"list": []})
        self.assertEqual(output, "")
