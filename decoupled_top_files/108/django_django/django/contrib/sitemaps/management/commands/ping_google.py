from django.contrib.sitemaps import ping_google
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument("sitemap_url", nargs="?")
        parser.add_argument("--sitemap-uses-http", action="store_true")

    def handle(self, *args, **options):
        """
        Handle the process of pinging Google with the given sitemap URL.
        
        Args:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments containing:
        - "sitemap_url": The URL of the sitemap to be pinged.
        - "sitemap_uses_http": A boolean indicating whether the sitemap uses HTTP or not. This is negated to determine if HTTPS should be used.
        
        Returns:
        None
        
        Notes:
        """

        ping_google(
            sitemap_url=options["sitemap_url"],
            sitemap_uses_https=not options["sitemap_uses_http"],
        )
