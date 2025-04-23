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
        
        This function renders a template with two variables, 'a' and 'b', both containing HTML content. The 'a' variable is a regular string, while 'b' is a marked safe string. The rendered output is expected to strip all HTML tags from both variables, resulting in plain text 'x y x y'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Variables:
        a (str): A string containing HTML content.
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
        """
        Tests the behavior of the `striptags` template filter on different inputs.
        
        This function renders a template named 'striptags02' with two context variables:
        - 'a': a string containing HTML tags.
        - 'b': a string containing HTML tags wrapped in `mark_safe` to prevent Django from escaping them.
        
        The expected output is "x y x y" because the `striptags` filter removes HTML tags and extracts the text content.
        
        Parameters:
        - None
        
        Returns:
        """

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
        self.assertEqual(
            striptags(
                lazystr(
                    'some <b>html</b> with <script>alert("Hello")</script> disallowed '
                    "<img /> tags"
                )
            ),
            'some html with alert("Hello") disallowed  tags',
        )
