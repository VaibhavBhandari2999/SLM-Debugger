from django.test import override_settings

from .cases import StaticFilesTestCase


class TestTemplateTag(StaticFilesTestCase):
    def test_template_tag(self):
        """
        Tests the behavior of the template tag for rendering static files.
        
        This function asserts the correct rendering of static file URLs. It checks three different scenarios:
        1. A non-existent file ('does/not/exist.png') should render as '/static/does/not/exist.png'.
        2. A regular file ('testfile.txt') should render as '/static/testfile.txt'.
        3. A file with special characters ('special?chars&quoted.html') should render with URL-encoded characters as '/static/special%
        """

        self.assertStaticRenders("does/not/exist.png", "/static/does/not/exist.png")
        self.assertStaticRenders("testfile.txt", "/static/testfile.txt")
        self.assertStaticRenders(
            "special?chars&quoted.html", "/static/special%3Fchars%26quoted.html"
        )

    @override_settings(
        STATICFILES_STORAGE="staticfiles_tests.storage.QueryStringStorage"
    )
    def test_template_tag_escapes(self):
        """
        Storage.url() should return an encoded path and might be overridden
        to also include a querystring. {% static %} escapes the URL to avoid
        raw '&', for example.
        """
        self.assertStaticRenders("a.html", "a.html?a=b&amp;c=d")
        self.assertStaticRenders("a.html", "a.html?a=b&c=d", autoescape=False)
