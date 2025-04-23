from django.apps import apps
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import modify_settings, override_settings


@override_settings(
    ROOT_URLCONF="flatpages_tests.urls",
    SITE_ID=1,
)
@modify_settings(
    INSTALLED_APPS={
        "append": ["django.contrib.sitemaps", "django.contrib.flatpages"],
    },
)
class FlatpagesSitemapTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class by clearing the cache of Site objects. This method is a class method and is intended to be used with test cases. It inherits from the setUpClass method of the superclass. The primary purpose is to ensure that tests do not interfere with each other due to caching issues in the contrib.sites framework.
        
        Parameters:
        - cls: The test class itself, passed as the first argument to class methods.
        
        Returns:
        - None: This method does not return any value. It performs in
        """

        super().setUpClass()
        # This cleanup is necessary because contrib.sites cache
        # makes tests interfere with each other, see #11505
        Site.objects.clear_cache()

    @classmethod
    def setUpTestData(cls):
        Site = apps.get_model("sites.Site")
        current_site = Site.objects.get_current()
        current_site.flatpage_set.create(url="/foo/", title="foo")
        current_site.flatpage_set.create(
            url="/private-foo/", title="private foo", registration_required=True
        )

    def test_flatpage_sitemap(self):
        """
        Tests the sitemap generation for flatpages.
        
        This function checks the sitemap for flatpages, ensuring that the correct URLs are included and excluded based on the settings. It sends a GET request to the sitemap XML endpoint and verifies that the expected URLs are present or absent in the response.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The response from the sitemap endpoint contains the URL for the public flatpage.
        - The response from the sitemap endpoint does not contain
        """

        response = self.client.get("/flatpages/sitemap.xml")
        self.assertIn(
            b"<url><loc>http://example.com/flatpage_root/foo/</loc></url>",
            response.getvalue(),
        )
        self.assertNotIn(
            b"<url><loc>http://example.com/flatpage_root/private-foo/</loc></url>",
            response.getvalue(),
        )
