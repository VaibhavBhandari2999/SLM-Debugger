from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class RandomTests(SimpleTestCase):
    @setup({"random01": "{{ a|random }} {{ b|random }}"})
    def test_random01(self):
        """
        Tests the rendering of a template with two variables 'a' and 'b'. Both variables contain lists with a single element each. The element in 'a' is a string with an HTML entity, and the element in 'b' is the same string but marked as safe. The function expects the rendered output to be 'a&amp;b a&b'.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None: This function asserts the expected output and does not return any value
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
        """
        Tests the rendering of a template with a custom context. The function takes a template name and a context dictionary as input. The context dictionary contains two keys, 'a' and 'b', each with a list of two elements. The elements in the lists are strings that may contain HTML entities. The function uses the engine to render the template with the given context. The output is expected to be the concatenation of the strings in the lists, with spaces in between. The function asserts that the rendered
        """

        output = self.engine.render_to_string(
            "random02", {"a": ["a&b", "a&b"], "b": [mark_safe("a&b"), mark_safe("a&b")]}
        )
        self.assertEqual(output, "a&b a&b")

    @setup({"empty_list": "{{ list|random }}"})
    def test_empty_list(self):
        output = self.engine.render_to_string("empty_list", {"list": []})
        self.assertEqual(output, "")
