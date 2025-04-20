from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class LastTests(SimpleTestCase):
    @setup({"last01": "{{ a|last }} {{ b|last }}"})
    def test_last01(self):
        """
        Tests the rendering of a template with the given context. The function takes a template name and a context dictionary as input. The context dictionary contains two keys, 'a' and 'b', each with a list as its value. The first element of each list is a string, and the second element is a marked safe string. The function renders the template with the provided context and asserts that the output matches the expected string "a&amp;b a&b".
        
        Parameters:
        - template_name (str):
        """

        output = self.engine.render_to_string(
            "last01", {"a": ["x", "a&b"], "b": ["x", mark_safe("a&b")]}
        )
        self.assertEqual(output, "a&amp;b a&b")

    @setup(
        {"last02": "{% autoescape off %}{{ a|last }} {{ b|last }}{% endautoescape %}"}
    )
    def test_last02(self):
        output = self.engine.render_to_string(
            "last02", {"a": ["x", "a&b"], "b": ["x", mark_safe("a&b")]}
        )
        self.assertEqual(output, "a&b a&b")

    @setup({"empty_list": "{% autoescape off %}{{ a|last }}{% endautoescape %}"})
    def test_empty_list(self):
        output = self.engine.render_to_string("empty_list", {"a": []})
        self.assertEqual(output, "")
