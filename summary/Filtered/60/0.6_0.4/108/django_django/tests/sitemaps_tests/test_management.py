from unittest import mock

from django.core.management import call_command

from .base import SitemapTestsBase


@mock.patch("django.contrib.sitemaps.management.commands.ping_google.ping_google")
class PingGoogleTests(SitemapTestsBase):
    def test_default(self, ping_google_func):
        call_command("ping_google")
        ping_google_func.assert_called_with(sitemap_url=None, sitemap_uses_https=True)

    def test_args(self, ping_google_func):
        """
        Tests the `ping_google` command with the specified sitemap URL and flags.
        
        Args:
        ping_google_func (Mock): A mock object representing the `ping_google` function call.
        
        This test function calls the `ping_google` command with the provided sitemap URL and the `--sitemap-uses-http` flag. It then verifies that the `ping_google` function was called with the correct parameters: the sitemap URL and the `sitemap_uses_https` set to `False`.
        """

        call_command("ping_google", "foo.xml", "--sitemap-uses-http")
        ping_google_func.assert_called_with(
            sitemap_url="foo.xml", sitemap_uses_https=False
        )
