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
        Sets up the test class by inheriting from the superclass's setUpClass method and clearing the cache for Site objects. This is necessary to prevent tests from interfering with each other, as the contrib.sites framework caches site data which can cause issues in a testing environment.
        
        Parameters:
        cls (class): The test class that this method is being defined for.
        
        Returns:
        None: This method does not return any value. It is a class method that is typically used to set up test fixtures before running
        """

        super().setUpClass()
        # This cleanup is necessary because contrib.sites cache
        # makes tests interfere with each other, see #11505
        Site.objects.clear_cache()

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the current site.
        
        This method creates two FlatPage instances for the current site:
        - A public FlatPage with the URL '/foo/' and title 'foo'.
        - A private FlatPage with the URL '/private-foo/', title 'private foo', and registration_required set to True.
        
        Parameters:
        cls (cls): The class object for the current test case.
        
        Returns:
        None: This method does not return any value. It sets up the test data for the current
        """

        Site = apps.get_model("sites.Site")
        current_site = Site.objects.get_current()
        current_site.flatpage_set.create(url="/foo/", title="foo")
        current_site.flatpage_set.create(
            url="/private-foo/", title="private foo", registration_required=True
        )

    def test_flatpage_sitemap(self):
        response = self.client.get("/flatpages/sitemap.xml")
        self.assertIn(
            b"<url><loc>http://example.com/flatpage_root/foo/</loc></url>",
            response.getvalue(),
        )
        self.assertNotIn(
            b"<url><loc>http://example.com/flatpage_root/private-foo/</loc></url>",
            response.getvalue(),
        )
