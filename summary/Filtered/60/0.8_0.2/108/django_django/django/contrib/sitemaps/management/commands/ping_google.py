from django.contrib.sitemaps import ping_google
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument("sitemap_url", nargs="?")
        parser.add_argument("--sitemap-uses-http", action="store_true")

    def handle(self, *args, **options):
        """
        Handle the process of pinging Google with the provided sitemap URL.
        
        This function is designed to ping Google's search engine with the specified sitemap URL to notify it of any changes in the site's content.
        
        Parameters:
        *args: Additional positional arguments (not used in this function).
        options (dict): A dictionary containing the following keys:
        - "sitemap_url" (str): The URL of the sitemap to be pinged.
        - "sitemap_uses_http" (bool
        """

        ping_google(
            sitemap_url=options["sitemap_url"],
            sitemap_uses_https=not options["sitemap_uses_http"],
        )
