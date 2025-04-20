from django.template.defaultfilters import striptags
from django.test import SimpleTestCase
from django.utils.functional import lazystr
from django.utils.safestring import mark_safe

from ..utils import setup


class StriptagsTests(SimpleTestCase):
    @setup({"striptags01": "{{ a|striptags }} {{ b|striptags }}"})
    def test_striptags01(self):
        """
        Tests the behavior of the `striptags` template filter on different inputs.
        
        This function renders a template with two variables: `a` and `b`. Variable `a` contains a string with HTML tags, while `b` contains the same string but wrapped in `mark_safe` to prevent Django from escaping it. The rendered output is then compared to the expected result, which is "x y x y".
        
        Parameters:
        - `self`: The instance of the test case class.
        
        Input:
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
        """
        Test the `striptags` function.
        
        This test checks if the `striptags` function correctly removes HTML tags, including script and img tags, and leaves other content intact.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> striptags('some <b>html</b> with <script>alert("You smell")</script> disallowed <img /> tags')
        'some html with alert("You smell") disallowed  tags'
        """

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
