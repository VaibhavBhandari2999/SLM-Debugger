from django.contrib.sitemaps import ping_google
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument("sitemap_url", nargs="?")
        parser.add_argument("--sitemap-uses-http", action="store_true")

    def handle(self, *args, **options):
        """
        Handle the process of submitting a sitemap to Google for indexing.
        
        This method is responsible for submitting a sitemap to Google's search console for indexing. It accepts the URL of the sitemap and a boolean indicating whether the sitemap uses HTTPS.
        
        Parameters:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments, expected to include:
        sitemap_url (str): The URL of the sitemap to be submitted.
        sitemap_uses
        """

        ping_google(
            sitemap_url=options["sitemap_url"],
            sitemap_uses_https=not options["sitemap_uses_http"],
        )
