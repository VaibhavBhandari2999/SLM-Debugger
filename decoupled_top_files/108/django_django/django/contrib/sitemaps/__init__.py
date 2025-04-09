import warnings
from urllib.parse import urlencode
from urllib.request import urlopen

from django.apps import apps as django_apps
from django.conf import settings
from django.core import paginator
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse
from django.utils import translation
from django.utils.deprecation import RemovedInDjango50Warning

PING_URL = "https://www.google.com/webmasters/tools/ping"


class SitemapNotFound(Exception):
    pass


def ping_google(sitemap_url=None, ping_url=PING_URL, sitemap_uses_https=True):
    """
    Alert Google that the sitemap for the current site has been updated.
    If sitemap_url is provided, it should be an absolute path to the sitemap
    for this site -- e.g., '/sitemap.xml'. If sitemap_url is not provided, this
    function will attempt to deduce it by using urls.reverse().
    """
    sitemap_full_url = _get_sitemap_full_url(sitemap_url, sitemap_uses_https)
    params = urlencode({"sitemap": sitemap_full_url})
    urlopen("%s?%s" % (ping_url, params))


def _get_sitemap_full_url(sitemap_url, sitemap_uses_https=True):
    """
    Generate a full URL for a sitemap.
    
    Args:
    sitemap_url (str): The URL of the sitemap.
    sitemap_uses_https (bool, optional): Whether the sitemap uses HTTPS. Defaults to True.
    
    Returns:
    str: The full URL of the sitemap.
    
    Raises:
    ImproperlyConfigured: If `django.contrib.sites` is not installed.
    SitemapNotFound: If no sitemap URL can be determined.
    
    Summary:
    """

    if not django_apps.is_installed("django.contrib.sites"):
        raise ImproperlyConfigured(
            "ping_google requires django.contrib.sites, which isn't installed."
        )

    if sitemap_url is None:
        try:
            # First, try to get the "index" sitemap URL.
            sitemap_url = reverse("django.contrib.sitemaps.views.index")
        except NoReverseMatch:
            try:
                # Next, try for the "global" sitemap URL.
                sitemap_url = reverse("django.contrib.sitemaps.views.sitemap")
            except NoReverseMatch:
                pass

    if sitemap_url is None:
        raise SitemapNotFound(
            "You didn't provide a sitemap_url, and the sitemap URL couldn't be "
            "auto-detected."
        )

    Site = django_apps.get_model("sites.Site")
    current_site = Site.objects.get_current()
    scheme = "https" if sitemap_uses_https else "http"
    return "%s://%s%s" % (scheme, current_site.domain, sitemap_url)


class Sitemap:
    # This limit is defined by Google. See the index documentation at
    # https://www.sitemaps.org/protocol.html#index.
    limit = 50000

    # If protocol is None, the URLs in the sitemap will use the protocol
    # with which the sitemap was requested.
    protocol = None

    # Enables generating URLs for all languages.
    i18n = False

    # Override list of languages to use.
    languages = None

    # Enables generating alternate/hreflang links.
    alternates = False

    # Add an alternate/hreflang link with value 'x-default'.
    x_default = False

    def _get(self, name, item, default=None):
        """
        Retrieve an attribute or call a method based on the given `name` and `item`.
        
        Args:
        name (str): The name of the attribute or method to retrieve.
        item: The item to pass to the method if it is callable.
        default: The value to return if the attribute does not exist.
        
        Returns:
        The value of the attribute or the result of calling the method with the given `item`.
        If the attribute does not exist, returns the specified `default
        """

        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            if self.i18n:
                # Split the (item, lang_code) tuples again for the location,
                # priority, lastmod and changefreq method calls.
                item, lang_code = item
            return attr(item)
        return attr

    def _languages(self):
        """
        Retrieve the list of languages.
        
        This method returns the list of languages either from the `languages` attribute
        or by generating it based on the `settings.LANGUAGES` tuple. If the `languages`
        attribute is not set, it constructs the list using a list comprehension that
        iterates over the `settings.LANGUAGES` tuple, extracting only the language codes.
        
        :return: A list of language codes.
        """

        if self.languages is not None:
            return self.languages
        return [lang_code for lang_code, _ in settings.LANGUAGES]

    def _items(self):
        """
        Generates a list of (item, lang_code) tuples for all items and languages if i18n is enabled, or returns the items directly otherwise.
        
        Args:
        self: The instance of the class containing the method.
        
        Returns:
        A list of (item, lang_code) tuples if i18n is enabled, or a list of items otherwise.
        
        Important Functions:
        - `_languages()`: Returns a list of language codes.
        - `items()`: Returns
        """

        if self.i18n:
            # Create (item, lang_code) tuples for all items and languages.
            # This is necessary to paginate with all languages already considered.
            items = [
                (item, lang_code)
                for lang_code in self._languages()
                for item in self.items()
            ]
            return items
        return self.items()

    def _location(self, item, force_lang_code=None):
        """
        Retrieve the location of an item.
        
        Args:
        item (tuple): A tuple containing the item and its language code.
        force_lang_code (str, optional): The language code to override the item's language code.
        
        Returns:
        str: The location of the item.
        
        Notes:
        - If `i18n` is enabled, the function will use the language code from the item or the forced language code to translate the item before retrieving its location.
        - The location
        """

        if self.i18n:
            obj, lang_code = item
            # Activate language from item-tuple or forced one before calling location.
            with translation.override(force_lang_code or lang_code):
                return self._get("location", item)
        return self._get("location", item)

    @property
    def paginator(self):
        return paginator.Paginator(self._items(), self.limit)

    def items(self):
        return []

    def location(self, item):
        return item.get_absolute_url()

    def get_protocol(self, protocol=None):
        """
        Determines the protocol for generating URLs.
        
        Args:
        protocol (str, optional): The protocol to use. Defaults to None.
        
        Returns:
        str: The protocol to use for generating URLs.
        
        Notes:
        - If `self.protocol` is not set and `protocol` is also not provided, a warning is issued about the default protocol changing from 'http' to 'https' in Django 5.0.
        - The function returns the provided `protocol`, `self.protocol
        """

        # Determine protocol
        if self.protocol is None and protocol is None:
            warnings.warn(
                "The default sitemap protocol will be changed from 'http' to "
                "'https' in Django 5.0. Set Sitemap.protocol to silence this "
                "warning.",
                category=RemovedInDjango50Warning,
                stacklevel=2,
            )
        # RemovedInDjango50Warning: when the deprecation ends, replace 'http'
        # with 'https'.
        return self.protocol or protocol or "http"

    def get_domain(self, site=None):
        """
        Retrieve the current domain.
        
        This function determines the domain based on the provided `site` parameter.
        If no `site` is provided, it attempts to retrieve the current site using Django's sites framework.
        If the sites framework is not installed, it raises an `ImproperlyConfigured` error.
        If no site can be retrieved, it also raises an `ImproperlyConfigured` error.
        
        Args:
        site (optional): A Site or RequestSite object.
        """

        # Determine domain
        if site is None:
            if django_apps.is_installed("django.contrib.sites"):
                Site = django_apps.get_model("sites.Site")
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured(
                    "To use sitemaps, either enable the sites framework or pass "
                    "a Site/RequestSite object in your view."
                )
        return site.domain

    def get_urls(self, page=1, site=None, protocol=None):
        """
        Generates URLs based on the given page number, site, and protocol.
        
        Args:
        page (int): The page number to generate URLs for.
        site (str, optional): The site domain to generate URLs for. Defaults to None.
        protocol (str, optional): The protocol to use for the URLs. Defaults to None.
        
        Returns:
        list: A list of generated URLs.
        
        Important Functions:
        - get_protocol: Determines the protocol to use for the URLs.
        """

        protocol = self.get_protocol(protocol)
        domain = self.get_domain(site)
        return self._urls(page, protocol, domain)

    def get_latest_lastmod(self):
        """
        Get the latest last modification timestamp.
        
        This method returns the latest last modification timestamp of the items
        in the collection. If the `lastmod` attribute is not set or is not callable,
        it returns `None`. If `lastmod` is callable, it attempts to find the maximum
        timestamp among all items by calling `lastmod(item)` for each item in the
        collection. If any call to `lastmod(item)` raises a `TypeError`, it returns
        """

        if not hasattr(self, "lastmod"):
            return None
        if callable(self.lastmod):
            try:
                return max([self.lastmod(item) for item in self.items()])
            except TypeError:
                return None
        else:
            return self.lastmod

    def _urls(self, page, protocol, domain):
        """
        Generates a list of URL objects with metadata for sitemap.xml.
        
        Args:
        page (int): The page number to fetch.
        protocol (str): The protocol to use for URLs ('http' or 'https').
        domain (str): The domain name for the URLs.
        
        Returns:
        list: A list of dictionaries containing URL information including location, lastmod, changefreq, and priority.
        """

        urls = []
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod

        paginator_page = self.paginator.page(page)
        for item in paginator_page.object_list:
            loc = f"{protocol}://{domain}{self._location(item)}"
            priority = self._get("priority", item)
            lastmod = self._get("lastmod", item)

            if all_items_lastmod:
                all_items_lastmod = lastmod is not None
                if all_items_lastmod and (
                    latest_lastmod is None or lastmod > latest_lastmod
                ):
                    latest_lastmod = lastmod

            url_info = {
                "item": item,
                "location": loc,
                "lastmod": lastmod,
                "changefreq": self._get("changefreq", item),
                "priority": str(priority if priority is not None else ""),
                "alternates": [],
            }

            if self.i18n and self.alternates:
                for lang_code in self._languages():
                    loc = f"{protocol}://{domain}{self._location(item, lang_code)}"
                    url_info["alternates"].append(
                        {
                            "location": loc,
                            "lang_code": lang_code,
                        }
                    )
                if self.x_default:
                    lang_code = settings.LANGUAGE_CODE
                    loc = f"{protocol}://{domain}{self._location(item, lang_code)}"
                    loc = loc.replace(f"/{lang_code}/", "/", 1)
                    url_info["alternates"].append(
                        {
                            "location": loc,
                            "lang_code": "x-default",
                        }
                    )

            urls.append(url_info)

        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls


class GenericSitemap(Sitemap):
    priority = None
    changefreq = None

    def __init__(self, info_dict, priority=None, changefreq=None, protocol=None):
        """
        Initializes an instance with a queryset, date field (optional), and optional parameters for priority, change frequency, and protocol.
        
        Args:
        info_dict (dict): A dictionary containing 'queryset' and optionally 'date_field'.
        priority (str, optional): The priority of the URL. Defaults to None.
        changefreq (str, optional): The change frequency of the URL. Defaults to None.
        protocol (str, optional): The protocol (http or https) of the
        """

        self.queryset = info_dict["queryset"]
        self.date_field = info_dict.get("date_field")
        self.priority = self.priority or priority
        self.changefreq = self.changefreq or changefreq
        self.protocol = self.protocol or protocol

    def items(self):
        # Make sure to return a clone; we don't want premature evaluation.
        return self.queryset.filter()

    def lastmod(self, item):
        """
        lastmod(item) -> datetime or None
        
        Determines the last modification time of an item based on either a specified date field or returns None.
        
        Parameters:
        item (object): The item whose last modification time is to be determined.
        
        Returns:
        datetime: The last modification time of the item if a date field is specified; otherwise, None.
        """

        if self.date_field is not None:
            return getattr(item, self.date_field)
        return None

    def get_latest_lastmod(self):
        """
        Retrieve the latest last modification date.
        
        This method fetches the latest last modification date from the queryset
        based on the specified date field. If a date field is provided, it orders
        the queryset in descending order by that field and returns the first value.
        Otherwise, it returns None.
        
        Args:
        None
        
        Returns:
        datetime: The latest last modification date or None if no date field is provided.
        """

        if self.date_field is not None:
            return (
                self.queryset.order_by("-" + self.date_field)
                .values_list(self.date_field, flat=True)
                .first()
            )
        return None
