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
        """
        Tests the urlizetrunc function with a template string that contains both unsafe and safe URLs.
        
        Parameters:
        - a (str): An unsafe URL with query parameters that need to be properly escaped and truncated.
        - b (SafeString): A safe URL with query parameters that should be properly escaped and truncated.
        
        Returns:
        - str: The rendered HTML with the URLs properly truncated and wrapped in anchor tags, ensuring that the unsafe URL is not vulnerable to XSS attacks.
        """

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
        """
        Test the urlizetrunc function with a short URL that is not truncated.
        
        This function tests the urlizetrunc function with a URL that is shorter than the specified truncation length. The function should not truncate the URL and should return a hyperlink with the URL as both the href and the displayed text.
        
        Parameters:
        url (str): The URL to be processed. In this case, the URL is "http://short.com/".
        truncation_length (int): The maximum length to
        """

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
        """
        Test the autoescaping behavior of the urlizetrunc function.
        
        This function checks if the urlizetrunc function correctly autoescapes HTML
        characters in the input string. The function takes a string and a maximum
        length as input and returns a truncated version of the string with URLs
        converted to clickable links. The test ensures that the function properly
        escapes special characters like '<', '&', and '"' to prevent HTML injection.
        
        Parameters:
        input_string (str): The input string containing potentially
        """

        self.assertEqual(
            urlizetrunc('foo<a href=" google.com ">bar</a>buz', 10),
            'foo&lt;a href=&quot; <a href="http://google.com" rel="nofollow">google.com'
            "</a> &quot;&gt;bar&lt;/a&gt;buz",
        )

    def test_autoescape_off(self):
        self.assertEqual(
            urlizetrunc('foo<a href=" google.com ">bar</a>buz', 9, autoescape=False),
            'foo<a href=" <a href="http://google.com" rel="nofollow">google.c…</a> ">'
            "bar</a>buz",
        )
