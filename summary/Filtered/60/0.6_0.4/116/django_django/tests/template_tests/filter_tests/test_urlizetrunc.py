from django.template.defaultfilters import urlizetrunc
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class UrlizetruncTests(SimpleTestCase):
    @setup(
        {
            "urlizetrunc01": (
                '{% autoescape off %}{{ a|urlizetrunc:"8" }} {{ b|urlizetrunc:"8" }}'
                "{% endautoescape %}"
            )
        }
    )
    def test_urlizetrunc01(self):
        output = self.engine.render_to_string(
            "urlizetrunc01",
            {
                "a": '"Unsafe" http://example.com/x=&y=',
                "b": mark_safe("&quot;Safe&quot; http://example.com?x=&amp;y="),
            },
        )
        self.assertEqual(
            output,
            '"Unsafe" '
            '<a href="http://example.com/x=&amp;y=" rel="nofollow">http://…</a> '
            "&quot;Safe&quot; "
            '<a href="http://example.com?x=&amp;y=" rel="nofollow">http://…</a>',
        )

    @setup({"urlizetrunc02": '{{ a|urlizetrunc:"8" }} {{ b|urlizetrunc:"8" }}'})
    def test_urlizetrunc02(self):
        """
        Tests the urlizetrunc02 template filter with different URL inputs.
        
        This function tests the `urlizetrunc02` template filter by rendering a template
        with two different URL inputs. The first URL is an unsafe URL with special
        characters, and the second URL is a safe URL with special characters, marked
        as safe.
        
        Parameters:
        - `a`: A string containing an unsafe URL with special characters.
        - `b`: A string containing a safe URL with special characters, marked
        """

        output = self.engine.render_to_string(
            "urlizetrunc02",
            {
                "a": '"Unsafe" http://example.com/x=&y=',
                "b": mark_safe("&quot;Safe&quot; http://example.com?x=&amp;y="),
            },
        )
        self.assertEqual(
            output,
            '&quot;Unsafe&quot; <a href="http://example.com/x=&amp;y=" rel="nofollow">'
            "http://…</a> "
            '&quot;Safe&quot; <a href="http://example.com?x=&amp;y=" rel="nofollow">'
            "http://…</a>",
        )


class FunctionTests(SimpleTestCase):
    def test_truncate(self):
        uri = "http://31characteruri.com/test/"
        self.assertEqual(len(uri), 31)

        self.assertEqual(
            urlizetrunc(uri, 31),
            '<a href="http://31characteruri.com/test/" rel="nofollow">'
            "http://31characteruri.com/test/</a>",
        )

        self.assertEqual(
            urlizetrunc(uri, 30),
            '<a href="http://31characteruri.com/test/" rel="nofollow">'
            "http://31characteruri.com/tes…</a>",
        )

        self.assertEqual(
            urlizetrunc(uri, 1),
            '<a href="http://31characteruri.com/test/" rel="nofollow">…</a>',
        )

    def test_overtruncate(self):
        self.assertEqual(
            urlizetrunc("http://short.com/", 20),
            '<a href="http://short.com/" rel="nofollow">http://short.com/</a>',
        )

    def test_query_string(self):
        self.assertEqual(
            urlizetrunc(
                "http://www.google.co.uk/search?hl=en&q=some+long+url&btnG=Search"
                "&meta=",
                20,
            ),
            '<a href="http://www.google.co.uk/search?hl=en&amp;q=some+long+url&amp;'
            'btnG=Search&amp;meta=" rel="nofollow">http://www.google.c…</a>',
        )

    def test_non_string_input(self):
        self.assertEqual(urlizetrunc(123, 1), "123")

    def test_autoescape(self):
        self.assertEqual(
            urlizetrunc('foo<a href=" google.com ">bar</a>buz', 10),
            'foo&lt;a href=&quot; <a href="http://google.com" rel="nofollow">google.com'
            "</a> &quot;&gt;bar&lt;/a&gt;buz",
        )

    def test_autoescape_off(self):
        """
        Test the behavior of the `urlizetrunc` function when `autoescape` is set to `False`.
        
        Parameters:
        - text (str): The input text containing URLs to be truncated and converted to HTML anchor tags.
        
        Returns:
        str: The processed text with URLs truncated and converted to HTML anchor tags, without escaping the HTML entities.
        
        Expected Output:
        'foo<a href=" <a href="http://google.com" rel="nofollow">google.c…</a> ">bar
        """

        self.assertEqual(
            urlizetrunc('foo<a href=" google.com ">bar</a>buz', 9, autoescape=False),
            'foo<a href=" <a href="http://google.com" rel="nofollow">google.c…</a> ">'
            "bar</a>buz",
        )
  "bar</a>buz",
        )
