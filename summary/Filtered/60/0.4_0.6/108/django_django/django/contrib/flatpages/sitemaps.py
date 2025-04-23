from django.apps import apps as django_apps
from django.contrib.sitemaps import Sitemap
from django.core.exceptions import ImproperlyConfigured


class FlatPageSitemap(Sitemap):
    def items(self):
        """
        Retrieve a list of flat pages for the current site.
        
        This method filters and returns flat pages that are not marked as requiring
        registration. It raises an `ImproperlyConfigured` exception if
        `django.contrib.sites` is not installed.
        
        Key Parameters:
        - None
        
        Returns:
        - QuerySet: A QuerySet of `FlatPage` objects that are not registration required.
        
        Raises:
        - ImproperlyConfigured: If `django.contrib.sites` is not installed.
        """

        if not django_apps.is_installed("django.contrib.sites"):
            raise ImproperlyConfigured(
                "FlatPageSitemap requires django.contrib.sites, which isn't installed."
            )
        Site = django_apps.get_model("sites.Site")
        current_site = Site.objects.get_current()
        return current_site.flatpage_set.filter(registration_required=False)
