from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class RandomTests(SimpleTestCase):
    @setup({"random01": "{{ a|random }} {{ b|random }}"})
    def test_random01(self):
        """
        Tests the rendering of a template with a string containing HTML entities.
        
        This function tests the rendering of a template named 'random01' with a context containing two lists. Each list contains a single element, which is a string with an HTML entity. The function uses the `render_to_string` method from an engine to render the template with the provided context. The output is then compared to the expected result to ensure that the HTML entities are correctly rendered.
        
        Parameters:
        - self: The test case instance
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
