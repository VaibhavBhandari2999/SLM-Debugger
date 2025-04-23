from django.contrib.sitemaps import ping_google
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument("sitemap_url", nargs="?")
        parser.add_argument("--sitemap-uses-http", action="store_true")

    def handle(self, *args, **options):
        """
        Handle the process of pinging Google with a sitemap.
        
        This function is responsible for pinging Google using the provided sitemap URL. The sitemap can either use HTTP or HTTPS, which is determined by the `sitemap_uses_http` option.
        
        Parameters:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments:
        sitemap_url (str): The URL of the sitemap to be pinged.
        sitemap_uses_http (
        """

        ping_google(
            sitemap_url=options["sitemap_url"],
            sitemap_uses_https=not options["sitemap_uses_http"],
        )
