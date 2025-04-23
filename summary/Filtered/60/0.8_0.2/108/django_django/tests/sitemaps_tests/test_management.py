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
        Test the `ping_google` command with the specified sitemap URL and flag.
        
        This function tests the `ping_google` command with the given sitemap URL and the `--sitemap-uses-http` flag. The `ping_google_func` is a mock function that is expected to be called with the provided sitemap URL and a boolean indicating whether the sitemap uses HTTPS.
        
        Parameters:
        ping_google_func (unittest.mock.Mock): A mock function to simulate the `ping_google` command.
        
        Key Parameters
        """

        call_command("ping_google", "foo.xml", "--sitemap-uses-http")
        ping_google_func.assert_called_with(
            sitemap_url="foo.xml", sitemap_uses_https=False
        )
