from django.template.defaultfilters import striptags
from django.test import SimpleTestCase
from django.utils.functional import lazystr
from django.utils.safestring import mark_safe

from ..utils import setup


class StriptagsTests(SimpleTestCase):
    @setup({"striptags01": "{{ a|striptags }} {{ b|striptags }}"})
    def test_striptags01(self):
        """
        Tests the behavior of the striptags template filter.
        
        This function renders a template with two variables, 'a' and 'b', each containing HTML content. The 'a' variable is a regular string, while 'b' is a marked safe string. The rendered output is expected to strip all HTML tags from both variables, leaving only the text content.
        
        Parameters:
        - self: The test case instance.
        
        Input:
        - 'a': A string containing HTML tags: "<a>x</a>
        """

        output = self.engine.render_to_string(
            "striptags01",
            {
                "a": "<a>x</a> <p><b>y</b></p>",
                "b": mark_safe("<a>x</a> <p><b>y</b></p>"),
            },
        )
        self.assertEqual(output, "x y x y")

    @setup(
        {
            "striptags02": (
                "{% autoescape off %}{{ a|striptags }} {{ b|striptags }}"
                "{% endautoescape %}"
            )
        }
    )
    def test_striptags02(self):
        output = self.engine.render_to_string(
            "striptags02",
            {
                "a": "<a>x</a> <p><b>y</b></p>",
                "b": mark_safe("<a>x</a> <p><b>y</b></p>"),
            },
        )
        self.assertEqual(output, "x y x y")


class FunctionTests(SimpleTestCase):
    def test_strip(self):
        self.assertEqual(
            striptags(
                'some <b>html</b> with <script>alert("You smell")</script> disallowed '
                "<img /> tags"
            ),
            'some html with alert("You smell") disallowed  tags',
        )

    def test_non_string_input(self):
        self.assertEqual(striptags(123), "123")

    def test_strip_lazy_string(self):
        """
        Test the `striptags` function on a lazy string.
        
        This test ensures that the `striptags` function correctly processes a lazy string containing HTML tags, script elements, and image tags. The function should remove all HTML tags, script elements, and image tags from the input string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Input:
        - A lazy string containing HTML tags, script elements, and image tags.
        
        Output:
        - A string with all HTML tags, script elements
        """

        self.assertEqual(
            striptags(
                lazystr(
                    'some <b>html</b> with <script>alert("Hello")</script> disallowed '
                    "<img /> tags"
                )
            ),
            'some html with alert("Hello") disallowed  tags',
        )
