from django.template.defaultfilters import slice_filter
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class SliceTests(SimpleTestCase):
    @setup({"slice01": '{{ a|slice:"1:3" }} {{ b|slice:"1:3" }}'})
    def test_slice01(self):
        output = self.engine.render_to_string(
            "slice01", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, "&amp;b &b")

    @setup(
        {
            "slice02": (
                '{% autoescape off %}{{ a|slice:"1:3" }} {{ b|slice:"1:3" }}'
                "{% endautoescape %}"
            )
        }
    )
    def test_slice02(self):
        """
        Tests the rendering of template strings with sliced variables. The function takes a Django template engine instance as `self.engine`. It renders the template 'slice02' with two context variables: 'a' and 'b'. Both 'a' and 'b' are set to the string "a&b", but 'b' is marked as safe to prevent HTML escaping. The expected output is "&b &b", as the slicing operation should return the substring "b" from both variables, and
        """

        output = self.engine.render_to_string(
            "slice02", {"a": "a&b", "b": mark_safe("a&b")}
        )
        self.assertEqual(output, "&b &b")


class FunctionTests(SimpleTestCase):
    def test_zero_length(self):
        self.assertEqual(slice_filter("abcdefg", "0"), "")

    def test_index(self):
        self.assertEqual(slice_filter("abcdefg", "1"), "a")

    def test_index_integer(self):
        self.assertEqual(slice_filter("abcdefg", 1), "a")

    def test_negative_index(self):
        self.assertEqual(slice_filter("abcdefg", "-1"), "abcdef")

    def test_range(self):
        self.assertEqual(slice_filter("abcdefg", "1:2"), "b")

    def test_range_multiple(self):
        self.assertEqual(slice_filter("abcdefg", "1:3"), "bc")

    def test_range_step(self):
        self.assertEqual(slice_filter("abcdefg", "0::2"), "aceg")

    def test_fail_silently(self):
        obj = object()
        self.assertEqual(slice_filter(obj, "0::2"), obj)
