from django.template.defaultfilters import first
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class FirstTests(SimpleTestCase):
    @setup({"first01": "{{ a|first }} {{ b|first }}"})
    def test_first01(self):
        output = self.engine.render_to_string(
            "first01", {"a": ["a&b", "x"], "b": [mark_safe("a&b"), "x"]}
        )
        self.assertEqual(output, "a&amp;b a&b")

    @setup(
        {
            "first02": (
                "{% autoescape off %}{{ a|first }} {{ b|first }}{% endautoescape %}"
            )
        }
    )
    def test_first02(self):
        """
        Tests the rendering of a template with two lists: 'a' and 'b'. The list 'a' contains a list with two elements, one of which is a string with an HTML entity ('a&b'). The list 'b' contains a similar list but with the same string as a Django SafeString. The function uses the engine to render the template 'first02' with the provided context. The expected output is the concatenation of the two elements in the list, with the
        """

        output = self.engine.render_to_string(
            "first02", {"a": ["a&b", "x"], "b": [mark_safe("a&b"), "x"]}
        )
        self.assertEqual(output, "a&b a&b")


class FunctionTests(SimpleTestCase):
    def test_list(self):
        self.assertEqual(first([0, 1, 2]), 0)

    def test_empty_string(self):
        self.assertEqual(first(""), "")

    def test_string(self):
        self.assertEqual(first("test"), "t")
