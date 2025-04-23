from django.contrib.sitemaps import ping_google
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument("sitemap_url", nargs="?")
        parser.add_argument("--sitemap-uses-http", action="store_true")

    def handle(self, *args, **options):
        """
        Handle the sitemap verification process.
        
        This function is responsible for verifying a sitemap with Google.
        
        Parameters:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments.
        sitemap_url (str): The URL of the sitemap to be verified.
        sitemap_uses_https (bool): Indicates whether the sitemap uses HTTPS. If False, it is assumed to use HTTP.
        
        This function does not return any value.
        """

        ping_google(
            sitemap_url=options["sitemap_url"],
            sitemap_uses_https=not options["sitemap_uses_http"],
        )
