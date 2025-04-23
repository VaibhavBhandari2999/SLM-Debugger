from datetime import datetime

from django.contrib.sitemaps import GenericSitemap
from django.test import ignore_warnings, override_settings
from django.utils.deprecation import RemovedInDjango50Warning

from .base import SitemapTestsBase
from .models import TestModel


@override_settings(ABSOLUTE_URL_OVERRIDES={})
class GenericViewsSitemapTests(SitemapTestsBase):
    def test_generic_sitemap_attributes(self):
        """
        Generates a test case for verifying the attributes of a GenericSitemap object.
        
        This function tests the attributes of a GenericSitemap object, ensuring that the specified attributes are set correctly. The attributes include date_field, priority, changefreq, and protocol. The function also verifies that the queryset attribute is set to the provided queryset.
        
        Parameters:
        - None (The function uses internal variables and does not accept any parameters).
        
        Returns:
        - None (The function performs assertions and does not return any value).
        """

        datetime_value = datetime.now()
        queryset = TestModel.objects.all()
        generic_sitemap = GenericSitemap(
            info_dict={
                "queryset": queryset,
                "date_field": datetime_value,
            },
            priority=0.6,
            changefreq="monthly",
            protocol="https",
        )
        attr_values = (
            ("date_field", datetime_value),
            ("priority", 0.6),
            ("changefreq", "monthly"),
            ("protocol", "https"),
        )
        for attr_name, expected_value in attr_values:
            with self.subTest(attr_name=attr_name):
                self.assertEqual(getattr(generic_sitemap, attr_name), expected_value)
        self.assertCountEqual(generic_sitemap.queryset, queryset)

    def test_generic_sitemap(self):
        "A minimal generic sitemap can be rendered"
        response = self.client.get("/generic/sitemap.xml")
        expected = ""
        for pk in TestModel.objects.values_list("id", flat=True):
            expected += "<url><loc>%s/testmodel/%s/</loc></url>" % (self.base_url, pk)
        expected_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            "%s\n"
            "</urlset>"
        ) % expected
        self.assertXMLEqual(response.content.decode(), expected_content)

    def test_generic_sitemap_lastmod(self):
        test_model = TestModel.objects.first()
        TestModel.objects.update(lastmod=datetime(2013, 3, 13, 10, 0, 0))
        response = self.client.get("/generic-lastmod/sitemap.xml")
        expected_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            "<url><loc>%s/testmodel/%s/</loc><lastmod>2013-03-13</lastmod></url>\n"
            "</urlset>"
        ) % (
            self.base_url,
            test_model.pk,
        )
        self.assertXMLEqual(response.content.decode(), expected_content)
        self.assertEqual(
            response.headers["Last-Modified"], "Wed, 13 Mar 2013 10:00:00 GMT"
        )

    def test_get_protocol_defined_in_constructor(self):
        for protocol in ["http", "https"]:
            with self.subTest(protocol=protocol):
                sitemap = GenericSitemap({"queryset": None}, protocol=protocol)
                self.assertEqual(sitemap.get_protocol(), protocol)

    def test_get_protocol_passed_as_argument(self):
        """
        Tests the `get_protocol` method of the `GenericSitemap` class.
        
        This method checks if the `get_protocol` method correctly returns the protocol passed as an argument.
        
        Parameters:
        - protocol (str): The protocol to be passed to the `get_protocol` method. It can be either 'http' or 'https'.
        
        Returns:
        - None: The function asserts the equality of the protocol passed and the one returned by the method.
        
        Example usage:
        ```python
        sitemap = GenericSitemap({"
        """

        sitemap = GenericSitemap({"queryset": None})
        for protocol in ["http", "https"]:
            with self.subTest(protocol=protocol):
                self.assertEqual(sitemap.get_protocol(protocol), protocol)

    @ignore_warnings(category=RemovedInDjango50Warning)
    def test_get_protocol_default(self):
        sitemap = GenericSitemap({"queryset": None})
        self.assertEqual(sitemap.get_protocol(), "http")

    def test_get_protocol_default_warning(self):
        """
        Tests the get_protocol method of the GenericSitemap class.
        
        This method checks the protocol used by the sitemap. By default, it uses 'http', but this will be changed to 'https' in Django 5.0. The method raises a RemovedInDjango50Warning if the protocol is not explicitly set by the user.
        
        Parameters:
        None
        
        Returns:
        str: The protocol used by the sitemap.
        
        Raises:
        RemovedInDjango50Warning: If the
        """

        sitemap = GenericSitemap({"queryset": None})
        msg = (
            "The default sitemap protocol will be changed from 'http' to "
            "'https' in Django 5.0. Set Sitemap.protocol to silence this "
            "warning."
        )
        with self.assertWarnsMessage(RemovedInDjango50Warning, msg):
            sitemap.get_protocol()

    def test_generic_sitemap_index(self):
        TestModel.objects.update(lastmod=datetime(2013, 3, 13, 10, 0, 0))
        response = self.client.get("/generic-lastmod/index.xml")
        expected_content = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap><loc>http://example.com/simple/sitemap-generic.xml</loc><lastmod>2013-03-13T10:00:00</lastmod></sitemap>
</sitemapindex>"""
        self.assertXMLEqual(response.content.decode("utf-8"), expected_content)
