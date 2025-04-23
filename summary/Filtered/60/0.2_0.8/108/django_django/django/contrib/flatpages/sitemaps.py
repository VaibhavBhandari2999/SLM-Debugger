from django.apps import apps as django_apps
from django.contrib.sitemaps import Sitemap
from django.core.exceptions import ImproperlyConfigured


class FlatPageSitemap(Sitemap):
    def items(self):
        """
        Retrieve a list of flat pages for the current site that are not registration required.
        
        This method filters and returns flat pages from the current site that do not require user registration.
        
        Key Parameters:
        - None
        
        Returns:
        - QuerySet: A QuerySet containing flat pages from the current site that are not registration required.
        
        Raises:
        - ImproperlyConfigured: If django.contrib.sites is not installed.
        
        Dependencies:
        - django.contrib.sites must be installed for this method to function correctly.
        """

        if not django_apps.is_installed("django.contrib.sites"):
            raise ImproperlyConfigured(
                "FlatPageSitemap requires django.contrib.sites, which isn't installed."
            )
        Site = django_apps.get_model("sites.Site")
        current_site = Site.objects.get_current()
        return current_site.flatpage_set.filter(registration_required=False)
