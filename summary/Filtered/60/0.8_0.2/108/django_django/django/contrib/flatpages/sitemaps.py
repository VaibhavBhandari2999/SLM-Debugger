from django.apps import apps as django_apps
from django.contrib.sitemaps import Sitemap
from django.core.exceptions import ImproperlyConfigured


class FlatPageSitemap(Sitemap):
    def items(self):
        """
        Generate a list of flat pages for the sitemap.
        
        This method retrieves flat pages from the current site that are not marked as
        registration_required. It first checks if `django.contrib.sites` is installed.
        If not, it raises an `ImproperlyConfigured` exception.
        
        Key Parameters:
        - None
        
        Returns:
        - A QuerySet of `FlatPage` objects from the current site that are not
        registration_required.
        
        Raises:
        - ImproperlyConfigured: If `django.contrib
        """

        if not django_apps.is_installed("django.contrib.sites"):
            raise ImproperlyConfigured(
                "FlatPageSitemap requires django.contrib.sites, which isn't installed."
            )
        Site = django_apps.get_model("sites.Site")
        current_site = Site.objects.get_current()
        return current_site.flatpage_set.filter(registration_required=False)
