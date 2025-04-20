from django.template.defaultfilters import first
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class FirstTests(SimpleTestCase):
    @setup({"first01": "{{ a|first }} {{ b|first }}"})
    def test_first01(self):
        """
        Tests the rendering of a template with two lists: 'a' and 'b'. The list 'a' contains a string with an HTML entity and a regular string, while 'b' contains a marked safe string and a regular string. The function expects the output to be 'a&amp;b a&b', where 'a&amp;b' is the HTML-escaped version of the string in list 'a' and 'a&b' is the unescaped version from list 'b'.
        
        Parameters
        """

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
        Tests the rendering of a template with two lists: 'a' and 'b'. The list 'a' contains a list with two elements, one of which is a string with an HTML entity, and the other is a regular string. The list 'b' contains a marked safe string and a regular string. The function expects the output to be the concatenation of the safe strings from both lists, which results in 'a&b a&b'.
        
        Parameters:
        - self: The test case
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
